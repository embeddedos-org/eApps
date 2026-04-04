import 'package:flutter/material.dart';

void main() => runApp(const EbotApp());

class EbotApp extends StatelessWidget {
  const EbotApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Assistant',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.blue,
        useMaterial3: true,
      ),
      home: const EbotHomeScreen(),
    );
  }
}

class EbotHomeScreen extends StatelessWidget {
  const EbotHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Assistant')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.apps, size: 64, color: Colors.blue),
            SizedBox(height: 16),
            Text('AI Assistant', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('EoS Mobile App - Coming Soon', style: TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}
