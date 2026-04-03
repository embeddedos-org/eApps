import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../../../core/widgets/loading_widget.dart';
import '../providers/ride_provider.dart';
import '../models/ride_model.dart';

class RideHistoryScreen extends ConsumerWidget {
  const RideHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final rides = ref.watch(userRidesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Ride History')),
      body: rides.when(
        data: (rideList) {
          if (rideList.isEmpty) {
            return const Center(child: Text('No rides yet'));
          }
          return ListView.builder(
            itemCount: rideList.length,
            itemBuilder: (context, index) {
              final ride = rideList[index];
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: _statusColor(ride.status).withOpacity(0.1),
                    child: Icon(
                      _vehicleIcon(ride.vehicleType),
                      color: _statusColor(ride.status),
                    ),
                  ),
                  title: Text(
                    ride.dropoffAddress,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  subtitle: Text(
                    '${AppDateUtils.formatDate(ride.createdAt)} • ${AppDateUtils.formatDistance(ride.distance)}',
                  ),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        AppDateUtils.formatCurrency(ride.fare),
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(
                        ride.status.name,
                        style: TextStyle(
                          fontSize: 12,
                          color: _statusColor(ride.status),
                        ),
                      ),
                    ],
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

  Color _statusColor(RideStatus status) {
    switch (status) {
      case RideStatus.completed:
        return AppColors.success;
      case RideStatus.cancelled:
        return AppColors.error;
      default:
        return AppColors.eRideColor;
    }
  }

  IconData _vehicleIcon(String type) {
    switch (type) {
      case 'bike':
        return Icons.two_wheeler;
      case 'taxi':
        return Icons.local_taxi;
      default:
        return Icons.directions_car;
    }
  }
}
