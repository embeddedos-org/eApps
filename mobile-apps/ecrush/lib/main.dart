import 'package:flutter/material.dart';

void main() => runApp(const EcrushApp());

class EcrushApp extends StatelessWidget {
  const EcrushApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Match-3 Puzzle Game',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.blue,
        useMaterial3: true,
      ),
      home: const EcrushHomeScreen(),
    );
  }
}

class EcrushHomeScreen extends StatelessWidget {
  const EcrushHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Match-3 Puzzle Game')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.apps, size: 64, color: Colors.blue),
            SizedBox(height: 16),
            Text('Match-3 Puzzle Game', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('EoS Mobile App - Coming Soon', style: TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}
