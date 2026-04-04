import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../../../core/widgets/loading_widget.dart';
import '../../../core/widgets/error_widget.dart';
import '../models/delivery_model.dart';
import '../providers/tracking_provider.dart';
import 'package:go_router/go_router.dart';

class DeliveryHistoryScreen extends ConsumerWidget {
  const DeliveryHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final historyAsync = ref.watch(deliveryHistoryProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Delivery History'),
      ),
      body: historyAsync.when(
        data: (deliveries) {
          if (deliveries.isEmpty) {
            return const EmptyStateWidget(
              title: 'No Delivery History',
              message: 'Delivered packages will appear here',
              icon: Icons.history_rounded,
            );
          }

          final grouped = <String, List<DeliveryModel>>{};
          for (final d in deliveries) {
            final key = AppDateUtils.formatShortDate(d.createdAt);
            grouped.putIfAbsent(key, () => []).add(d);
          }

          return ListView.builder(
            padding: const EdgeInsets.only(top: 8, bottom: 24),
            itemCount: grouped.length,
            itemBuilder: (context, sectionIndex) {
              final date = grouped.keys.elementAt(sectionIndex);
              final items = grouped[date]!;

              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
                    child: Text(
                      date,
                      style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textSecondary,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ),
                  ...items.map((delivery) => _HistoryTile(delivery: delivery)),
                ],
              );
            },
          );
        },
        loading: () => const LoadingWidget(message: 'Loading history...'),
        error: (error, _) => AppErrorWidget(
          title: 'Failed to load history',
          message: error.toString(),
          onRetry: () => ref.invalidate(deliveryHistoryProvider),
        ),
      ),
    );
  }
}

class _HistoryTile extends StatelessWidget {
  final DeliveryModel delivery;

  const _HistoryTile({required this.delivery});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: AppColors.delivered.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: const Icon(
            Icons.check_circle_rounded,
            color: AppColors.delivered,
            size: 24,
          ),
        ),
        title: Text(
          delivery.packageName,
          style: const TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 15,
          ),
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 4),
          child: Row(
            children: [
              _CarrierBadge(carrier: delivery.carrier),
              const SizedBox(width: 8),
              Flexible(
                child: Text(
                  delivery.trackingNumber,
                  style: const TextStyle(
                    fontSize: 12,
                    color: AppColors.textHint,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              'Delivered',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: AppColors.delivered,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              delivery.estimatedDelivery != null
                  ? AppDateUtils.formatShortDate(delivery.estimatedDelivery!)
                  : AppDateUtils.formatShortDate(delivery.createdAt),
              style: const TextStyle(
                fontSize: 11,
                color: AppColors.textHint,
              ),
            ),
          ],
        ),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        onTap: () => context.push('/tracking/${delivery.id}'),
      ),
    );
  }
}

class _CarrierBadge extends StatelessWidget {
  final String carrier;

  const _CarrierBadge({required this.carrier});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: AppColors.primary.withOpacity(0.08),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        carrier,
        style: const TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w600,
          color: AppColors.primary,
        ),
      ),
    );
  }
}
