import 'package:flutter/material.dart';

void main() => runApp(const EgalleryApp());

class EgalleryApp extends StatelessWidget {
  const EgalleryApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Photo Gallery',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.blue,
        useMaterial3: true,
      ),
      home: const EgalleryHomeScreen(),
    );
  }
}

class EgalleryHomeScreen extends StatelessWidget {
  const EgalleryHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Photo Gallery')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.apps, size: 64, color: Colors.blue),
            SizedBox(height: 16),
            Text('Photo Gallery', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('EoS Mobile App - Coming Soon', style: TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}
