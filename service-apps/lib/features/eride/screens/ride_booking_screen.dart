import 'package:flutter/material.dart';

class RideBookingScreen extends StatelessWidget {
  const RideBookingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Book a Ride')),
      body: const Center(child: Text('Ride Booking')),
    );
  }
}
