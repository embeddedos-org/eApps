import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../../../core/widgets/loading_widget.dart';
import '../providers/tracking_provider.dart';
import '../models/delivery_model.dart';

class DeliveryHistoryScreen extends ConsumerWidget {
  const DeliveryHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final deliveries = ref.watch(allDeliveriesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Delivery History')),
      body: deliveries.when(
        data: (list) {
          if (list.isEmpty) {
            return const Center(child: Text('No deliveries yet'));
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: list.length,
            itemBuilder: (context, index) {
              final d = list[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  onTap: () => context.push('/track/detail/${d.id}'),
                  leading: CircleAvatar(
                    backgroundColor: _statusColor(d.status).withOpacity(0.1),
                    child: Icon(
                      Icons.inventory_2,
                      color: _statusColor(d.status),
                    ),
                  ),
                  title: Text(
                    d.trackingNumber,
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 13,
                    ),
                  ),
                  subtitle: Text(
                    '${d.carrier} • ${d.type.name.toUpperCase()} • ${AppDateUtils.timeAgo(d.createdAt)}',
                  ),
                  trailing: Text(
                    d.status.name,
                    style: TextStyle(
                      fontSize: 12,
                      color: _statusColor(d.status),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              );
            },
          );
        },
        loading: () => const AppLoadingWidget(),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }

  Color _statusColor(DeliveryStatus status) {
    switch (status) {
      case DeliveryStatus.delivered:
        return AppColors.success;
      case DeliveryStatus.failed:
        return AppColors.error;
      case DeliveryStatus.outForDelivery:
        return AppColors.success;
      default:
        return AppColors.eTrackColor;
    }
  }
}
