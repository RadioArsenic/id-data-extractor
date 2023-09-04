import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:camera/camera.dart';

import 'camera_screen.dart';

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

String stringResponse = "";

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late CameraController _controller;

  Future apicall() async {
    http.Response response;
    // http://10.0.2.2:5000/api?query=2
    response = await http.get(Uri.parse("https://reqres.in/api/users?page=2"));
    if (response.statusCode == 200) {
      setState(() {
        stringResponse = response.body;
      });
    }
  }

  @override
  void initState() {
    apicall();
    super.initState();
    _controller = CameraController(cameras[0], ResolutionPreset.max);
    _controller.initialize().then((_) {
      if (!mounted) {
        return;
      }
      setState(() {});
    }).catchError((Object e) {
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
      appBar: AppBar(title: Text("OCR program")),
      body:
          Stack(
            children: [
              Container(
                  height: double.infinity,
                  child: CameraPreview(_controller),
                ),
              Center(
                child:
                  Container(
                    height: 200,
                width: 300,
                decoration: BoxDecoration(
                    border: Border.all(color: Colors.white),
                    ),
                child: Center(
                  // child: Text(stringResponse.toString()),
                )),
                ),
                Column(
                  mainAxisAlignment: MainAxisAlignment.end,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Center(
                      child: Container(
                        margin: EdgeInsets.all(20.0),
                        child: MaterialButton(onPressed: () async {
                          if (!_controller.value.isInitialized) {
                            return null;
                          }
                          if (_controller.value.isTakingPicture) {
                            return null;
                          }

                          try {
                            await _controller.setFlashMode(FlashMode.auto);
                            XFile file = await _controller.takePicture();
                            Navigator.push(
                                context,
                                MaterialPageRoute(
                                    builder: (context) => ImagePreview(file)));
                          } on CameraException catch (e) {
                            debugPrint("Error occured while taking picture: $e");
                            return null;
                          }
                        },
                        color: Colors.white,
                        child:Text("Take a picture"),
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
