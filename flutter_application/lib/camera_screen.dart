import 'dart:io';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';


//image viewing page of the app, app redirects to here once image taken
class ImagePreview extends StatefulWidget {
  ImagePreview(this.file, {super.key});
  
  // XFile contains the path property to the image
  XFile file;

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
        appBar: AppBar(title: Text("Image Preview")),
        body: Center(
          // displaying of image taken
          child:Column(
            children: <Widget>[
              Image.file(picture), // Checking if jsonData is null before trying to access its properties
              // Checking if jsonData is null before trying to access its properties

              Column(
                children: [
                  Text('Name:'),
                  Text('Age: '),
                  // Add more Text widgets here to display additional JSON data
                ],
              ),
          ],

              
          ) 
        ), 

        );
  }
}
