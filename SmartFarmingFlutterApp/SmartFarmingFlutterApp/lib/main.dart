
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  final String streamlitUrl = "https://smatfarm.streamlit.app/";

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Farming Assistant',
      home: Scaffold(
        appBar: AppBar(title: Text('Smart Farming Assistant')),
        body: SafeArea(
          child: WebView(
            initialUrl: streamlitUrl,
            javascriptMode: JavascriptMode.unrestricted,
          ),
        ),
      ),
    );
  }
}
