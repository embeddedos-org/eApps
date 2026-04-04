import 'package:flutter/material.dart';
import '../models/tracking_enums.dart';

class StatusBadge extends StatelessWidget {
  final TrackingStatus status;
  final bool showEmoji;

  const StatusBadge({super.key, required this.status, this.showEmoji = true});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: status.color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: status.color.withOpacity(0.3)),
      ),
      child: Text(
        showEmoji ? '${status.emoji} ${status.label}' : status.label,
        style: TextStyle(
          color: status.color,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
