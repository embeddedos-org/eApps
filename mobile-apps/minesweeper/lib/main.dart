import 'package:flutter/material.dart';

void main() => runApp(const MinesweeperApp());

class MinesweeperApp extends StatelessWidget {
  const MinesweeperApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Minesweeper Game',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.blue,
        useMaterial3: true,
      ),
      home: const MinesweeperHomeScreen(),
    );
  }
}

class MinesweeperHomeScreen extends StatelessWidget {
  const MinesweeperHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Minesweeper Game')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.apps, size: 64, color: Colors.blue),
            SizedBox(height: 16),
            Text('Minesweeper Game', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('EoS Mobile App - Coming Soon', style: TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}
