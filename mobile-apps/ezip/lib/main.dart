import 'package:flutter/material.dart';

void main() => runApp(const EzipApp());

class EzipApp extends StatelessWidget {
  const EzipApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Archive Manager',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.blue,
        useMaterial3: true,
      ),
      home: const EzipHomeScreen(),
    );
  }
}

class EzipHomeScreen extends StatelessWidget {
  const EzipHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Archive Manager')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.apps, size: 64, color: Colors.blue),
            SizedBox(height: 16),
            Text('Archive Manager', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('EoS Mobile App - Coming Soon', style: TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}
