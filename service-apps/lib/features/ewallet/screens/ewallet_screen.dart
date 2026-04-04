import 'package:flutter/material.dart';

class EWalletScreen extends StatelessWidget {
  const EWalletScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('eWallet')),
      body: const Center(child: Text('Digital Wallet')),
    );
  }
}
