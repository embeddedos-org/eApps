import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../providers/ride_provider.dart';

class RideHomeScreen extends ConsumerWidget {
  const RideHomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeRide = ref.watch(activeRideProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('eRide'),
        backgroundColor: AppColors.eRideColor.withOpacity(0.05),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => context.push('/ride/history'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Active ride banner
            activeRide.when(
              data: (ride) {
                if (ride == null) return const SizedBox.shrink();
                return GestureDetector(
                  onTap: () => context.push('/ride/track/${ride.id}'),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: AppColors.eRideColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppColors.eRideColor),
                    ),
                    child: Row(
                      children: [
                        const Icon(
                          Icons.directions_car,
                          color: AppColors.eRideColor,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Active Ride',
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              Text(
                                ride.dropoffAddress,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ),
                        ),
                        const Icon(Icons.arrow_forward_ios, size: 16),
                      ],
                    ),
                  ),
                );
              },
              loading: () => const SizedBox.shrink(),
              error: (_, __) => const SizedBox.shrink(),
            ),

            // Map placeholder
            Container(
              height: 200,
              width: double.infinity,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.map, size: 48, color: Colors.grey),
                    SizedBox(height: 8),
                    Text('Map View', style: TextStyle(color: Colors.grey)),
                    Text(
                      '(Google Maps integration)',
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            Text(
              'Where to?',
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),

            // Quick destination input
            GestureDetector(
              onTap: () => context.push('/ride/book'),
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 14,
                ),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.search, color: Colors.grey),
                    SizedBox(width: 12),
                    Text(
                      'Enter destination...',
                      style: TextStyle(color: Colors.grey),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            Text(
              'Choose ride type',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),

            Row(
              children: [
                _VehicleOption(
                  icon: Icons.directions_car,
                  label: 'Car',
                  price: '\$8-12',
                  onTap: () => context.push('/ride/book'),
                ),
                const SizedBox(width: 12),
                _VehicleOption(
                  icon: Icons.two_wheeler,
                  label: 'Bike',
                  price: '\$3-6',
                  onTap: () => context.push('/ride/book'),
                ),
                const SizedBox(width: 12),
                _VehicleOption(
                  icon: Icons.local_taxi,
                  label: 'Taxi',
                  price: '\$10-15',
                  onTap: () => context.push('/ride/book'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _VehicleOption extends StatelessWidget {
  final IconData icon;
  final String label;
  final String price;
  final VoidCallback onTap;

  const _VehicleOption({
    required this.icon,
    required this.label,
    required this.price,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey[300]!),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: [
              Icon(icon, size: 32, color: AppColors.eRideColor),
              const SizedBox(height: 8),
              Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
              Text(
                price,
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
