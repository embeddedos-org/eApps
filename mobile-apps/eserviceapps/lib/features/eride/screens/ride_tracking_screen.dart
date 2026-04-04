import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../../../core/widgets/loading_widget.dart';
import '../providers/ride_provider.dart';
import '../models/ride_model.dart';

class RideTrackingScreen extends ConsumerWidget {
  final String rideId;
  const RideTrackingScreen({super.key, required this.rideId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ride = ref.watch(rideDetailProvider(rideId));

    return Scaffold(
      appBar: AppBar(title: const Text('Ride Tracking')),
      body: ride.when(
        data: (r) {
          if (r == null) return const Center(child: Text('Ride not found'));
          return Column(
            children: [
              // Map placeholder
              Expanded(
                flex: 2,
                child: Container(
                  color: Colors.grey[200],
                  child: const Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.map, size: 64, color: Colors.grey),
                        Text('Live Map Tracking'),
                      ],
                    ),
                  ),
                ),
              ),
              // Ride info card
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                  boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 10)],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _StatusBadge(status: r.status),
                        Text(
                          'ETA: ${r.estimatedMinutes} min',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                      ],
                    ),
                    const Divider(height: 24),
                    _LocationRow(
                      icon: Icons.my_location,
                      color: AppColors.success,
                      label: 'Pickup',
                      address: r.pickupAddress,
                    ),
                    const SizedBox(height: 12),
                    _LocationRow(
                      icon: Icons.location_on,
                      color: AppColors.error,
                      label: 'Drop-off',
                      address: r.dropoffAddress,
                    ),
                    const Divider(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Vehicle: ${r.vehicleType.toUpperCase()}'),
                        Text('Distance: ${AppDateUtils.formatDistance(r.distance)}'),
                        Text('Fare: ${AppDateUtils.formatCurrency(r.fare)}', style: const TextStyle(fontWeight: FontWeight.bold)),
                      ],
                    ),
                    if (r.status != RideStatus.completed && r.status != RideStatus.cancelled) ...[
                      const SizedBox(height: 16),
                      SizedBox(
                        width: double.infinity,
                        child: OutlinedButton(
                          onPressed: () => ref.read(rideServiceProvider).cancelRide(r.id),
                          style: OutlinedButton.styleFrom(foregroundColor: AppColors.error),
                          child: const Text('Cancel Ride'),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          );
        },
        loading: () => const AppLoadingWidget(),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  final RideStatus status;
  const _StatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    final colors = {
      RideStatus.requested: AppColors.warning,
      RideStatus.accepted: AppColors.info,
      RideStatus.driverEnRoute: AppColors.info,
      RideStatus.arrived: AppColors.success,
      RideStatus.inProgress: AppColors.eRideColor,
      RideStatus.completed: AppColors.success,
      RideStatus.cancelled: AppColors.error,
    };
    final labels = {
      RideStatus.requested: 'Requesting...',
      RideStatus.accepted: 'Driver Accepted',
      RideStatus.driverEnRoute: 'Driver En Route',
      RideStatus.arrived: 'Driver Arrived',
      RideStatus.inProgress: 'In Progress',
      RideStatus.completed: 'Completed',
      RideStatus.cancelled: 'Cancelled',
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: (colors[status] ?? Colors.grey).withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        labels[status] ?? status.name,
        style: TextStyle(color: colors[status], fontWeight: FontWeight.bold, fontSize: 13),
      ),
    );
  }
}

class _LocationRow extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String label;
  final String address;

  const _LocationRow({required this.icon, required this.color, required this.label, required this.address});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
              Text(address, style: const TextStyle(fontWeight: FontWeight.w500)),
            ],
          ),
        ),
      ],
    );
  }
}
