import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/loading_widget.dart';
import '../providers/tracking_provider.dart';
import '../models/delivery_model.dart';

class TrackHomeScreen extends ConsumerWidget {
  const TrackHomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final deliveries = ref.watch(activeDeliveriesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('eTrack'),
        backgroundColor: AppColors.eTrackColor.withOpacity(0.05),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => context.push('/track/history'),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppColors.eTrackColor,
        onPressed: () => context.push('/track/add'),
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text(
          'Track Package',
          style: TextStyle(color: Colors.white),
        ),
      ),
      body: deliveries.when(
        data: (list) {
          if (list.isEmpty) {
            return const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.local_shipping_outlined,
                    size: 64,
                    color: AppColors.textSecondary,
                  ),
                  SizedBox(height: 16),
                  Text('No active deliveries'),
                  SizedBox(height: 8),
                  Text(
                    'Tap + to track a package',
                    style: TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: list.length,
            itemBuilder: (context, index) {
              final d = list[index];
              return _DeliveryCard(delivery: d);
            },
          );
        },
        loading: () => const AppLoadingWidget(),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }
}

class _DeliveryCard extends StatelessWidget {
  final DeliveryModel delivery;
  const _DeliveryCard({required this.delivery});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => context.push('/track/detail/${delivery.id}'),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Icon(
                        _carrierIcon(delivery.carrier),
                        color: AppColors.eTrackColor,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        delivery.carrier,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  _StatusChip(status: delivery.status),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                delivery.trackingNumber,
                style: const TextStyle(fontFamily: 'monospace', fontSize: 13),
              ),
              if (delivery.description.isNotEmpty) ...[
                const SizedBox(height: 4),
                Text(
                  delivery.description,
                  style: TextStyle(color: Colors.grey[600]),
                ),
              ],
              if (delivery.events.isNotEmpty) ...[
                const Divider(height: 16),
                Row(
                  children: [
                    const Icon(Icons.update, size: 16, color: Colors.grey),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        delivery.events.last.description,
                        style: const TextStyle(fontSize: 13),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  IconData _carrierIcon(String carrier) {
    if (carrier.toLowerCase().contains('fedex')) return Icons.flight;
    if (carrier.toLowerCase().contains('ups')) return Icons.local_shipping;
    if (carrier.toLowerCase().contains('post')) return Icons.mail;
    return Icons.inventory_2;
  }
}

class _StatusChip extends StatelessWidget {
  final DeliveryStatus status;
  const _StatusChip({required this.status});

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
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: (colors[status] ?? Colors.grey).withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        status.name,
        style: TextStyle(
          fontSize: 12,
          color: colors[status],
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}
