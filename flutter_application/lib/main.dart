import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:camera/camera.dart';
import 'dart:io';

//late - variables are value is assigned l
late List<CameraDescription> cameras;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  cameras = await availableCameras();
  HttpOverrides.global = MyHttpOverrides();
  // await addSelfSignedCertificate();
  runApp(const MyApp());
}

class MyHttpOverrides extends HttpOverrides {
  @override
  HttpClient createHttpClient(SecurityContext? context) {
    return super.createHttpClient(context)
      ..badCertificateCallback =
          (X509Certificate cert, String host, int port) => true;
  }
}

// Future<bool> addSelfSignedCertificate() async {
//   ByteData data = await rootBundle.load('assets/raw/cert.pem');
//   SecurityContext context = SecurityContext.defaultContext;
//   context.setTrustedCertificatesBytes(data.buffer.asUint8List());
//   return true;
// }
class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.blue),
      home: HomeScreen(),
    );
  }
}

//variable to hold the response from the server
var stringResponse;
var selectedState;

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

// code for the homescreen of the app
class _HomeScreenState extends State<HomeScreen> {
  late CameraController _controller;
  String? _selectedOption; // Moved outside of the build method
  final List<String> _options = [
    'Western Australia',
    'New South Wales',
    'Victoria',
    'Northern Territory',
    'Australian Capital Territory',
    'Southern Australia',
    'Tasmania',
    'Queensland',
    'PASSPORT'
  ];

  @override
  void initState() {
    super.initState();
    _controller = CameraController(cameras[0], ResolutionPreset.max);
    _controller.initialize().then((_) {
      if (!mounted) return;
      setState(() {});
    }).catchError((e) {
      if (e is CameraException) {
        // Handle camera exception
        print(e.description);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("OCR program")),
      body: Stack(
        children: [
          SizedBox(
            height: double.infinity,
            child: CameraPreview(_controller),
          ),
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              DropdownButton<String>(
                value: _selectedOption,
                items: _options.map((String value) {
                  return DropdownMenuItem<String>(
                    value: value,
                    child: Text(value),
                  );
                }).toList(),
                hint: Text(_selectedOption ?? 'Select an Option'),
                onChanged: (newValue) {
                  setState(() {
                    _selectedOption = newValue;
                    selectedState = _selectedOption;

                  });
                },
              ),
              Center(
                child: Container(
                  height: 200,
                  width: 300,
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.white),
                  ),
                ),
              ),
              Center(
                child: Container(
                  // adding a margin
                  margin: const EdgeInsets.all(20.0),
                  child: MaterialButton(
                    onPressed: () async {
                      // camera controller check for whether it is running
                      if (!_controller.value.isInitialized) {
                        return;
                      }
                      // checking if currently taking a picture already
                      if (_controller.value.isTakingPicture) {
                        return;
                      }

                      try {
                        // the taking of a picture
                        XFile file = await _controller.takePicture();

                        // Uploading the image to the api
                        await uploadImage(File(file.path));

                        //changes to a image view mode
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => ImagePreview(file),
                          ),
                        );
                      } on CameraException catch (e) {
                        debugPrint("Error occurred while taking picture: $e");
                        return null;
                      }
                    },
                    color: Colors.white,
                    child: const Text("Take a picture"),
                  ),
                ),
              )
            ],
          )
        ],
      ),
    );
  }
}

Future<void> uploadImage(File imageFile) async {
  // The URL for the image upload, here this was the local flask app used
  var uri = Uri.parse("https://10.0.2.2:5000/upload");

  //usage of mulipart to transfer the image data
  var request = http.MultipartRequest('POST', uri)
    ..headers['x-api-key'] = 'JPkxhc9cGFv35OWu267fsx8R6uZj29GL'
    ..fields['selectedOption'] = selectedState!
    ..files.add(await http.MultipartFile.fromPath('file', imageFile.path));

  var streamedResponse = await request.send();
  var response = await http.Response.fromStream(streamedResponse);
  stringResponse = jsonDecode(response.body) as Map<String, dynamic>;

  // messages of success/failure of request
  if (response.statusCode == 200) {
    print('Successfully sent!');
  } else {
    print('error!');
  }
}

//image viewing page of the app, app redirects to here once image taken
class ImagePreview extends StatefulWidget {
  ImagePreview(this.file, {super.key});

  // XFile contains the path property to the image
  XFile file;
  Map<String, dynamic>? jsonData;

  @override
  State<ImagePreview> createState() => _ImagePreviewState();
}

class _ImagePreviewState extends State<ImagePreview> {
  @override
  Widget build(BuildContext context) {
    // displaying of response from the picture
    return Scaffold(
      // "Image Preview" at the top
      appBar: AppBar(
          title: Text(stringResponse.containsKey('error')
              ? "Poor image, please retake photo"
              : "Retake photo")),
      body: Center(
          // displaying of image taken
          child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          // Checking if response is null before trying to access its properties
          if (stringResponse != Null && !stringResponse.containsKey('error'))
            Column(
              children: stringResponse!.entries
                  .map<Widget>(
                    (entry) => Text('${entry.key}: ${entry.value}'),
                  )
                  .toList(),
            )
          else
            Column(children: [Text(" Invalid image ")]),
        ],
      )),
    );
  }
}
