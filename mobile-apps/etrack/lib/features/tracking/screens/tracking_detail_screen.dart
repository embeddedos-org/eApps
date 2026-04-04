import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../../../core/widgets/loading_widget.dart';
import '../../../core/widgets/error_widget.dart';
import '../models/delivery_model.dart';
import '../providers/tracking_provider.dart';

class TrackingDetailScreen extends ConsumerWidget {
  final String deliveryId;

  const TrackingDetailScreen({super.key, required this.deliveryId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final deliveryAsync = ref.watch(deliveryDetailProvider(deliveryId));

    return deliveryAsync.when(
      data: (delivery) {
        if (delivery == null) {
          return Scaffold(
            appBar: AppBar(title: const Text('Not Found')),
            body: const AppErrorWidget(
              title: 'Package not found',
              message: 'This tracking entry may have been removed.',
              icon: Icons.search_off_rounded,
            ),
          );
        }
        return _DetailView(delivery: delivery);
      },
      loading: () => Scaffold(
        appBar: AppBar(title: const Text('Loading...')),
        body: const LoadingWidget(message: 'Loading tracking details...'),
      ),
      error: (error, _) => Scaffold(
        appBar: AppBar(title: const Text('Error')),
        body: AppErrorWidget(
          title: 'Failed to load details',
          message: error.toString(),
          onRetry: () => ref.invalidate(deliveryDetailProvider(deliveryId)),
        ),
      ),
    );
  }
}

class _DetailView extends ConsumerWidget {
  final DeliveryModel delivery;

  const _DetailView({required this.delivery});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statusColor = AppColors.statusColor(delivery.status.name);

    return Scaffold(
      appBar: AppBar(
        title: Text(delivery.packageName),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Refresh',
            onPressed: () async {
              final service = ref.read(trackingServiceProvider);
              await service.refreshTracking(delivery.id);
            },
          ),
          PopupMenuButton<String>(
            onSelected: (value) async {
              if (value == 'copy') {
                await Clipboard.setData(
                    ClipboardData(text: delivery.trackingNumber));
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: const Text('Tracking number copied!'),
                      behavior: SnackBarBehavior.floating,
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10)),
                    ),
                  );
                }
              } else if (value == 'delete') {
                final confirm = await showDialog<bool>(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('Remove Package'),
                    content: const Text(
                        'Are you sure you want to stop tracking this package?'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(ctx, false),
                        child: const Text('Cancel'),
                      ),
                      TextButton(
                        onPressed: () => Navigator.pop(ctx, true),
                        style: TextButton.styleFrom(foregroundColor: AppColors.error),
                        child: const Text('Remove'),
                      ),
                    ],
                  ),
                );
                if (confirm == true && context.mounted) {
                  final service = ref.read(trackingServiceProvider);
                  await service.removeTracking(delivery.id);
                  if (context.mounted) Navigator.pop(context);
                }
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'copy',
                child: ListTile(
                  leading: Icon(Icons.copy_rounded),
                  title: Text('Copy Tracking #'),
                  contentPadding: EdgeInsets.zero,
                ),
              ),
              const PopupMenuItem(
                value: 'delete',
                child: ListTile(
                  leading: Icon(Icons.delete_outline_rounded, color: AppColors.error),
                  title: Text('Remove', style: TextStyle(color: AppColors.error)),
                  contentPadding: EdgeInsets.zero,
                ),
              ),
            ],
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            _PackageInfoCard(delivery: delivery, statusColor: statusColor),
            _ProgressStepper(delivery: delivery),
            if (delivery.latestEvent != null)
              _MapPlaceholder(location: delivery.latestEvent!.location),
            _TrackingTimeline(events: delivery.events),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }
}

class _PackageInfoCard extends StatelessWidget {
  final DeliveryModel delivery;
  final Color statusColor;

  const _PackageInfoCard({required this.delivery, required this.statusColor});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [statusColor.withOpacity(0.12), statusColor.withOpacity(0.03)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: statusColor.withOpacity(0.2)),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Icon(Icons.local_shipping_rounded,
                    color: statusColor, size: 28),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: statusColor.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        delivery.status.label,
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: statusColor,
                        ),
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      delivery.packageName,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w700,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          const Divider(height: 1),
          const SizedBox(height: 16),
          _InfoRow(
            icon: Icons.local_shipping_outlined,
            label: 'Carrier',
            value: delivery.carrier,
          ),
          const SizedBox(height: 10),
          _InfoRow(
            icon: Icons.tag_rounded,
            label: 'Tracking #',
            value: delivery.trackingNumber,
          ),
          const SizedBox(height: 10),
          _InfoRow(
            icon: Icons.calendar_today_rounded,
            label: 'Est. Delivery',
            value: AppDateUtils.estimatedDeliveryText(delivery.estimatedDelivery),
            valueColor: delivery.status == DeliveryStatus.outForDelivery
                ? AppColors.outForDelivery
                : null,
          ),
          const SizedBox(height: 10),
          _InfoRow(
            icon: Icons.access_time_rounded,
            label: 'Added',
            value: AppDateUtils.formatRelative(delivery.createdAt),
          ),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color? valueColor;

  const _InfoRow({
    required this.icon,
    required this.label,
    required this.value,
    this.valueColor,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 16, color: AppColors.textSecondary),
        const SizedBox(width: 10),
        Text(
          label,
          style: const TextStyle(
            fontSize: 13,
            color: AppColors.textSecondary,
          ),
        ),
        const Spacer(),
        Flexible(
          child: Text(
            value,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: valueColor ?? AppColors.textPrimary,
            ),
            textAlign: TextAlign.end,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}

class _ProgressStepper extends StatelessWidget {
  final DeliveryModel delivery;

  const _ProgressStepper({required this.delivery});

  @override
  Widget build(BuildContext context) {
    final steps = [
      ('Ordered', Icons.receipt_long_rounded),
      ('Shipped', Icons.inventory_2_rounded),
      ('In Transit', Icons.flight_takeoff_rounded),
      ('Out for Delivery', Icons.delivery_dining_rounded),
      ('Delivered', Icons.check_circle_rounded),
    ];

    final currentStep = delivery.status == DeliveryStatus.exception
        ? -1
        : delivery.status.stepIndex;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.divider),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Delivery Progress',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 20),
          if (delivery.status == DeliveryStatus.exception)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.exception.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Row(
                children: [
                  Icon(Icons.warning_amber_rounded,
                      color: AppColors.exception, size: 24),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Delivery exception — contact carrier for details',
                      style: TextStyle(
                        color: AppColors.exception,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            )
          else
            ...List.generate(steps.length, (index) {
              final isCompleted = index <= currentStep;
              final isCurrent = index == currentStep;
              final isLast = index == steps.length - 1;
              final color = isCompleted
                  ? AppColors.primary
                  : AppColors.divider;

              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Column(
                    children: [
                      Container(
                        width: 36,
                        height: 36,
                        decoration: BoxDecoration(
                          color: isCompleted
                              ? AppColors.primary
                              : AppColors.surface,
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: color,
                            width: isCurrent ? 3 : 2,
                          ),
                          boxShadow: isCurrent
                              ? [
                                  BoxShadow(
                                    color: AppColors.primary.withOpacity(0.3),
                                    blurRadius: 8,
                                    spreadRadius: 1,
                                  )
                                ]
                              : null,
                        ),
                        child: Icon(
                          isCompleted ? steps[index].$2 : steps[index].$2,
                          size: 18,
                          color: isCompleted ? Colors.white : AppColors.textHint,
                        ),
                      ),
                      if (!isLast)
                        Container(
                          width: 2,
                          height: 32,
                          color: isCompleted && index < currentStep
                              ? AppColors.primary
                              : AppColors.divider,
                        ),
                    ],
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Padding(
                      padding: EdgeInsets.only(
                          top: 6, bottom: isLast ? 0 : 18),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            steps[index].$1,
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight:
                                  isCurrent ? FontWeight.w700 : FontWeight.w500,
                              color: isCompleted
                                  ? AppColors.textPrimary
                                  : AppColors.textHint,
                            ),
                          ),
                          if (isCurrent && delivery.latestEvent != null)
                            Padding(
                              padding: const EdgeInsets.only(top: 2),
                              child: Text(
                                delivery.latestEvent!.description,
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: AppColors.textSecondary,
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
                ],
              );
            }),
        ],
      ),
    );
  }
}

class _MapPlaceholder extends StatelessWidget {
  final String location;

  const _MapPlaceholder({required this.location});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      height: 180,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.divider),
        color: AppColors.surface,
      ),
      child: Stack(
        children: [
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.map_rounded,
                  size: 48,
                  color: AppColors.primary,
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.location_on, size: 16, color: AppColors.primary),
                    const SizedBox(width: 4),
                    Text(
                      location,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                const Text(
                  'Current package location',
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          Positioned(
            top: 8,
            right: 8,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.open_in_new_rounded,
                      size: 12, color: AppColors.primary),
                  SizedBox(width: 4),
                  Text(
                    'Open Map',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: AppColors.primary,
                    ),
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

class _TrackingTimeline extends StatelessWidget {
  final List<TrackingEvent> events;

  const _TrackingTimeline({required this.events});

  @override
  Widget build(BuildContext context) {
    if (events.isEmpty) return const SizedBox.shrink();

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.divider),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.timeline_rounded, size: 20, color: AppColors.primary),
              SizedBox(width: 8),
              Text(
                'Tracking History',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...List.generate(events.length, (index) {
            final event = events[index];
            final isFirst = index == 0;
            final isLast = index == events.length - 1;

            return Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Column(
                  children: [
                    Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: isFirst ? AppColors.primary : AppColors.divider,
                        shape: BoxShape.circle,
                        border: isFirst
                            ? Border.all(color: AppColors.primary, width: 2)
                            : null,
                      ),
                    ),
                    if (!isLast)
                      Container(
                        width: 1.5,
                        height: 56,
                        color: AppColors.divider,
                      ),
                  ],
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Padding(
                    padding: EdgeInsets.only(bottom: isLast ? 0 : 16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          event.description,
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight:
                                isFirst ? FontWeight.w600 : FontWeight.w400,
                            color: isFirst
                                ? AppColors.textPrimary
                                : AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Icon(Icons.location_on_outlined,
                                size: 12, color: AppColors.textHint),
                            const SizedBox(width: 4),
                            Flexible(
                              child: Text(
                                event.location,
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: AppColors.textHint,
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Icon(Icons.access_time_rounded,
                                size: 12, color: AppColors.textHint),
                            const SizedBox(width: 4),
                            Text(
                              AppDateUtils.formatDateTime(event.timestamp),
                              style: const TextStyle(
                                fontSize: 12,
                                color: AppColors.textHint,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            );
          }),
        ],
      ),
    );
  }
}
