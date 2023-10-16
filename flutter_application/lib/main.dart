import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:camera/camera.dart';
import 'dart:io';

//late - variables are value is assigned l
late List<CameraDescription> cameras;

//global variable to hold the response from the server, variable for state
var stringResponse;
var selectedState;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  cameras = await availableCameras();
  //for accepting self-signed certificates
  HttpOverrides.global = MyHttpOverrides();
  runApp(MaterialApp(home: StartingPage(), debugShowCheckedModeBanner: false));
}

// changing the http setting to accept our self-signed certificates
class MyHttpOverrides extends HttpOverrides {
  @override
  HttpClient createHttpClient(SecurityContext? context) {
    return super.createHttpClient(context)
      ..badCertificateCallback =
          (X509Certificate cert, String host, int port) => true;
  }
}

class StartingPage extends StatefulWidget {
  @override
  _StartingPageState createState() => _StartingPageState();
}

// Page with country and state selection
class _StartingPageState extends State<StartingPage> {
  String? CountrySelected;
  String? stateOrPassportSelected;
  final List<String> _options = [
    'Australia',
    // Add other countries in the future
  ];

  final Map<String, List<String>> _subOptions = {
    'Australia': [
      'Western Australia',
      'New South Wales',
      'Victoria',
      'Northern Territory',
      'Australian Capital Territory',
      'Southern Australia',
      'Tasmania',
      'Queensland',
      'PASSPORT'
    ],
    // Map other countries to their respective states in the future
  };

  @override
  Widget build(BuildContext context) {
    var subOptionDropdown = CountrySelected == null
        ? Container()
        : DropdownButton<String>(
            value: stateOrPassportSelected,
            items: _subOptions[CountrySelected]!.map((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: Text(value),
              );
            }).toList(),
            hint: Text('Select a country'),
            onChanged: (newValue) {
              setState(() {
                stateOrPassportSelected = newValue;
              });
            },
          );
    return Scaffold(
      appBar: AppBar(title: Text('Select a State or passport')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            DropdownButton<String>(
              value: CountrySelected,
              items: _options.map((String value) {
                return DropdownMenuItem<String>(
                  value: value,
                  child: Text(value),
                );
              }).toList(),
              hint: Text('Select an Option'),
              onChanged: (newValue) {
                setState(() {
                  CountrySelected = newValue;
                  stateOrPassportSelected =
                      null; // Reset the sub-option when the main option changes
                });
              },
            ),
            subOptionDropdown,
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          if (CountrySelected != null && stateOrPassportSelected != null) {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => IDTakingScreen(
                    CountrySelected: CountrySelected,
                    stateOrPassportSelected: stateOrPassportSelected),
              ),
            );
          }
        },
        child: Icon(Icons.arrow_forward),
        tooltip: 'Proceed',
      ),
    );
  }
}

class IDTakingScreen extends StatefulWidget {
  final String? CountrySelected;
  final String? stateOrPassportSelected;
  const IDTakingScreen(
      {Key? key, this.CountrySelected, this.stateOrPassportSelected})
      : super(key: key);

  @override
  _IDTakingScreenState createState() => _IDTakingScreenState();
}

// IDTakingScreen of the app
class _IDTakingScreenState extends State<IDTakingScreen> {
  late CameraController _controller;
  String? get CountrySelected => widget.CountrySelected;
  String? get stateOrPassportSelected => widget.stateOrPassportSelected;

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
      appBar: AppBar(title: const Text("Place ID within box")),
      body: Stack(
        children: [
          SizedBox(
            height: double.infinity,
            child: CameraPreview(_controller),
          ),
          Column(
            // aligning contents to be in the middle
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Center(
                // drawing of a border for potential area to take image of id
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

                      // checking if a CountrySelected is selected
                      if (stateOrPassportSelected == null) {
                        return;
                      }
                      selectedState = stateOrPassportSelected;

                      try {
                        // the taking of a picture
                        XFile file = await _controller.takePicture();

                        // Uploading the image to the api
                        await extractData(File(file.path));

                        //changes to a image view mode
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => ResultPage(file),
                          ),
                        );
                      } on CameraException catch (e) {
                        debugPrint("Error occurred while taking picture: $e");
                        return;
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

Future<void> extractData(File imageFile) async {
  // The URL for the image upload, here this was the local flask app used
  var uri = Uri.parse("https://10.0.2.2:5000/extract_data");

  //usage of mulipart to transfer the image data
  var request = http.MultipartRequest('POST', uri)
    ..headers['x-api-key'] = 'JPkxhc9cGFv35OWu267fsx8R6uZj29GL'
    ..fields['selectedOption'] = selectedState!
    ..files.add(await http.MultipartFile.fromPath('file', imageFile.path));

  // Sending the request and getting the response
  var streamedResponse = await request.send();
  var response = await http.Response.fromStream(streamedResponse);
  // Decoding the JSON response
  stringResponse = jsonDecode(response.body) as Map<String, dynamic>;

  // messages of success/failure of request
  if (response.statusCode == 200) {
    print('Successfully sent!');
  } else {
    print('error!');
  }
}

//image viewing page of the app, app redirects to here once image taken
class ResultPage extends StatefulWidget {
  ResultPage(this.file, {super.key});

  // XFile contains the path property to the image
  XFile file;
  Map<String, dynamic>? jsonData;

  @override
  State<ResultPage> createState() => _ResultPageState();
}

class _ResultPageState extends State<ResultPage> {
  @override
  Widget build(BuildContext context) {
    // Function to build a row for each key-value pair
    Widget _buildRow(String key, dynamic value) {
      return Padding(
        padding: const EdgeInsets.all(8.0),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            Text(
              key,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 18,
              ),
            ),
            Text(
              value.toString(),
              style: TextStyle(fontSize: 16),
            ),
          ],
        ),
      );
    }

    // displaying of response from the picture
    return Scaffold(
      // result message printed as the title of page
      appBar: AppBar(
          title: Text(stringResponse.containsKey('error')
              ? "Poor image, please retake photo"
              : "Retake photo?")),
      body: Center(
          // displaying result of from image taken
          child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          // Checking if response is null before trying to access its properties
          if (stringResponse != null && stringResponse.containsKey('success'))
            Column(
              children: <Widget>[
                _buildRow('Name', stringResponse['name']),
                _buildRow('Expiry Date', stringResponse['expiry_date']),
                _buildRow('Date of Birth', stringResponse['date_of_birth']),
                _buildRow('Address', stringResponse['address']),
              ],
            )
          else if (stringResponse.containsKey('error'))
            const Column(children: [Text(" Invalid image ")]),
        ],
      )),
    );
  }
}
