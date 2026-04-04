import 'package:flutter/material.dart';
import '../models/tracking_enums.dart';

class CarrierIcon extends StatelessWidget {
  final Carrier carrier;
  final double size;

  const CarrierIcon({super.key, required this.carrier, this.size = 24});

  @override
  Widget build(BuildContext context) {
    return Icon(carrier.icon, size: size);
  }
}
