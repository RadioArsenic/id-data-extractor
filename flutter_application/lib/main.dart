import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:camera/camera.dart';
import 'dart:io';

//late - variables are value is assigned l
late List<CameraDescription> cameras;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  cameras = await availableCameras();
  runApp(const MyApp());
}

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

var stringResponse;
// currently a url to api for random user generator
// const apiURL = "http://10.0.2.2:5000/api?query=2";

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

// code for the homescreen of the app
class _HomeScreenState extends State<HomeScreen> {
  // camera variable
  late CameraController _controller;

  //api call function
  // Future apicall() async {
  //   http.Response response;
  //   response = await http.get(Uri.parse(apiURL));
  //   if (response.statusCode == 200) {
  //     setState(() {
  //       //setting the response of the apicall to stringResponse
  //       stringResponse = response.body;
  //     });
  //   }
  // }

  @override
  void initState() {
    // apicall();
    super.initState();
    _controller = CameraController(cameras[0], ResolutionPreset.max);

    // initialize the first available camera
    _controller.initialize().then((_) {
      if (!mounted) {
        return;
      }
      setState(() {});
    }).catchError((Object e) {
      //checking for camera access error
      if (e is CameraException) {
        switch (e.code) {
          case 'CameraAccessDenited':
            print("acces was denied");
            break;
          default:
            print(e.description);
            break;
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      //text and bars of the app (decorations)
      appBar: AppBar(title: Text("OCR program")),
      body: Stack(
        children: [
          SizedBox(
            height: double.infinity,
            child: CameraPreview(_controller),
          ),
          Center(
            child: Container(
              height: 200,
              width: 300,
              decoration: BoxDecoration(
                // the white box for the card outline
                border: Border.all(color: Colors.white),
              ),
              // displays response of above api call "apiURL" variable
              // child: Center(
              //     child: Text(stringResponse.toString()),
              // )
            ),
          ),
          Column(
            // aligning of the page content
            mainAxisAlignment: MainAxisAlignment.end,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
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
  var uri = Uri.parse("http://10.0.2.2:5000/upload");

  //usage of mulipart to transfer the image data
  var request = http.MultipartRequest('POST', uri)
    ..headers['x-api-key'] = 'JPkxhc9cGFv35OWu267fsx8R6uZj29GL'
    ..files.add(await http.MultipartFile.fromPath('file', imageFile.path));

  var streamedResponse = await request.send();
  var response= await http.Response.fromStream(streamedResponse);
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
    // retreving of image
    File picture = File(widget.file.path);
    return Scaffold(
      // "Image Preview" at the top
      appBar: AppBar(title: Text("Retake photo")),
      body: Center(
          // displaying of image taken
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          
          // Checking if response is null before trying to access its properties
          if (stringResponse != Null)
            Column(
            children: stringResponse!.entries
                    .map<Widget>(
                      (entry) => Text('${entry.key}: ${entry.value}'),
                    )
                    .toList(),
          ),
          
          
        ],
      )),
    );
  }
}
