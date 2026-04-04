import 'package:flutter/material.dart';
import '../models/tracking_item.dart';
import '../utils/date_utils.dart';
import 'status_badge.dart';
import 'carrier_icon.dart';

class TrackingCard extends StatelessWidget {
  final TrackingItem item;
  final VoidCallback onTap;

  const TrackingCard({super.key, required this.item, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  CarrierIcon(carrier: item.carrier),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item.label.isNotEmpty
                              ? item.label
                              : item.carrier.label,
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 15,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 2),
                        Text(
                          item.trackingNumber,
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey[600],
                            fontFamily: 'monospace',
                          ),
                        ),
                      ],
                    ),
                  ),
                  StatusBadge(status: item.status),
                ],
              ),
              if (item.statusExplanation.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  item.statusExplanation,
                  style: TextStyle(fontSize: 13, color: Colors.grey[700]),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              if (item.events.isNotEmpty) ...[
                const SizedBox(height: 6),
                Row(
                  children: [
                    Icon(Icons.access_time, size: 14, color: Colors.grey[500]),
                    const SizedBox(width: 4),
                    Text(
                      AppDateUtils.timeAgo(item.events.first.timestamp),
                      style: TextStyle(fontSize: 12, color: Colors.grey[500]),
                    ),
                    if (item.events.first.location.isNotEmpty) ...[
                      const SizedBox(width: 12),
                      Icon(Icons.location_on,
                          size: 14, color: Colors.grey[500]),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          item.events.first.location,
                          style:
                              TextStyle(fontSize: 12, color: Colors.grey[500]),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ],
                ),
              ],
              if (item.tags.isNotEmpty) ...[
                const SizedBox(height: 8),
                Wrap(
                  spacing: 6,
                  children: item.tags
                      .map((tag) => Chip(
                            label: Text(tag.label,
                                style: const TextStyle(fontSize: 11)),
                            backgroundColor: tag.color.withOpacity(0.1),
                            side: BorderSide(color: tag.color.withOpacity(0.3)),
                            padding: EdgeInsets.zero,
                            materialTapTargetSize:
                                MaterialTapTargetSize.shrinkWrap,
                            visualDensity: VisualDensity.compact,
                          ))
                      .toList(),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
