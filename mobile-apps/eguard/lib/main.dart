import 'package:flutter/material.dart';

void main() => runApp(const EguardApp());

class EguardApp extends StatelessWidget {
  const EguardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Security & Privacy',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.blue,
        useMaterial3: true,
      ),
      home: const EguardHomeScreen(),
    );
  }
}

class EguardHomeScreen extends StatelessWidget {
  const EguardHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Security & Privacy')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.apps, size: 64, color: Colors.blue),
            SizedBox(height: 16),
            Text('Security & Privacy', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('EoS Mobile App - Coming Soon', style: TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}
