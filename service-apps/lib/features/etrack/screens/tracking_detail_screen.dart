import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../../../core/widgets/loading_widget.dart';
import '../providers/tracking_provider.dart';
import '../models/delivery_model.dart';

class TrackingDetailScreen extends ConsumerWidget {
  final String deliveryId;
  const TrackingDetailScreen({super.key, required this.deliveryId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final delivery = ref.watch(deliveryDetailProvider(deliveryId));

    return Scaffold(
      appBar: AppBar(title: const Text('Tracking Details')),
      body: delivery.when(
        data: (d) {
          if (d == null) return const Center(child: Text('Delivery not found'));
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Tracking info card
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              d.carrier,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 18,
                              ),
                            ),
                            _StatusBadge(status: d.status),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            const Icon(
                              Icons.qr_code,
                              size: 16,
                              color: Colors.grey,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              d.trackingNumber,
                              style: const TextStyle(fontFamily: 'monospace'),
                            ),
                          ],
                        ),
                        if (d.description.isNotEmpty) ...[
                          const SizedBox(height: 8),
                          Text(
                            d.description,
                            style: TextStyle(color: Colors.grey[600]),
                          ),
                        ],
                        if (d.estimatedDelivery.isNotEmpty) ...[
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              const Icon(
                                Icons.calendar_today,
                                size: 16,
                                color: AppColors.eTrackColor,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                'Est. delivery: ${d.estimatedDelivery.substring(0, 10)}',
                              ),
                            ],
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  'Tracking Timeline',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                // Timeline
                ...d.events.reversed.toList().asMap().entries.map((entry) {
                  final index = entry.key;
                  final event = entry.value;
                  final isFirst = index == 0;
                  return _TimelineItem(
                    event: event,
                    isFirst: isFirst,
                    isLast: index == d.events.length - 1,
                  );
                }),
                if (d.events.isEmpty)
                  const Center(child: Text('No tracking events yet')),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () {
                      ref.read(trackingServiceProvider).deleteTracking(d.id);
                      Navigator.of(context).pop();
                    },
                    icon: const Icon(Icons.delete_outline),
                    label: const Text('Remove Tracking'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppColors.error,
                    ),
                  ),
                ),
              ],
            ),
          );
        },
        loading: () => const AppLoadingWidget(),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  final DeliveryStatus status;
  const _StatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    final colors = {
      DeliveryStatus.pending: AppColors.warning,
      DeliveryStatus.pickedUp: AppColors.info,
      DeliveryStatus.inTransit: AppColors.eTrackColor,
      DeliveryStatus.outForDelivery: AppColors.success,
      DeliveryStatus.delivered: AppColors.success,
      DeliveryStatus.failed: AppColors.error,
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: (colors[status] ?? Colors.grey).withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        status.name,
        style: TextStyle(
          color: colors[status],
          fontWeight: FontWeight.bold,
          fontSize: 13,
        ),
      ),
    );
  }
}

class _TimelineItem extends StatelessWidget {
  final TrackingEvent event;
  final bool isFirst;
  final bool isLast;

  const _TimelineItem({
    required this.event,
    required this.isFirst,
    required this.isLast,
  });

  @override
  Widget build(BuildContext context) {
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 40,
            child: Column(
              children: [
                Container(
                  width: 12,
                  height: 12,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isFirst ? AppColors.eTrackColor : Colors.grey[300],
                    border: Border.all(
                      color: isFirst
                          ? AppColors.eTrackColor
                          : Colors.grey[400]!,
                      width: 2,
                    ),
                  ),
                ),
                if (!isLast)
                  Expanded(child: Container(width: 2, color: Colors.grey[300])),
              ],
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(bottom: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    event.status,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: isFirst ? AppColors.eTrackColor : Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(event.description, style: const TextStyle(fontSize: 13)),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(
                        Icons.location_on,
                        size: 14,
                        color: Colors.grey[500],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        event.location,
                        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      ),
                      const SizedBox(width: 12),
                      Icon(
                        Icons.access_time,
                        size: 14,
                        color: Colors.grey[500],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        AppDateUtils.formatDateTime(event.timestamp),
                        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
