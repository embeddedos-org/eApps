import 'package:flutter/material.dart';

class AdminContentScreen extends StatelessWidget {
  const AdminContentScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Content Management')),
      body: const Center(child: Text('Admin Content')),
    );
  }
}
