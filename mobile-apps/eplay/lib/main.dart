import 'package:flutter/material.dart';

void main() => runApp(const EplayApp());

class EplayApp extends StatelessWidget {
  const EplayApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Media Player',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.blue,
        useMaterial3: true,
      ),
      home: const EplayHomeScreen(),
    );
  }
}

class EplayHomeScreen extends StatelessWidget {
  const EplayHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Media Player')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.apps, size: 64, color: Colors.blue),
            SizedBox(height: 16),
            Text('Media Player', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('EoS Mobile App - Coming Soon', style: TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}
