import 'package:flutter/material.dart';

void main() => runApp(const EclockApp());

class EclockApp extends StatelessWidget {
  const EclockApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'World Clock & Alarms',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.blue,
        useMaterial3: true,
      ),
      home: const EclockHomeScreen(),
    );
  }
}

class EclockHomeScreen extends StatelessWidget {
  const EclockHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('World Clock & Alarms')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.apps, size: 64, color: Colors.blue),
            SizedBox(height: 16),
            Text('World Clock & Alarms', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('EoS Mobile App - Coming Soon', style: TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}
