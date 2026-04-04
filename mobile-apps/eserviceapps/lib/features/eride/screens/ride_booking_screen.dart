import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../providers/ride_provider.dart';

class RideBookingScreen extends ConsumerStatefulWidget {
  const RideBookingScreen({super.key});

  @override
  ConsumerState<RideBookingScreen> createState() => _RideBookingScreenState();
}

class _RideBookingScreenState extends ConsumerState<RideBookingScreen> {
  final _pickupController = TextEditingController();
  final _dropoffController = TextEditingController();
  String _selectedVehicle = 'car';
  bool _isBooking = false;

  @override
  void dispose() {
    _pickupController.dispose();
    _dropoffController.dispose();
    super.dispose();
  }

  Future<void> _bookRide() async {
    if (_pickupController.text.isEmpty || _dropoffController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter pickup and drop-off locations')),
      );
      return;
    }

    final user = ref.read(currentUserProvider).value;
    if (user == null) return;

    setState(() => _isBooking = true);
    try {
      final service = ref.read(rideServiceProvider);
      final distance = 5.0 + (DateTime.now().millisecond % 10);
      final fare = service.calculateFare(_selectedVehicle, distance);
      final eta = service.estimateTime(distance);

      final rideId = await service.requestRide(
        userId: user.uid,
        vehicleType: _selectedVehicle,
        pickupLat: 37.7749,
        pickupLng: -122.4194,
        pickupAddress: _pickupController.text,
        dropoffLat: 37.7849,
        dropoffLng: -122.4094,
        dropoffAddress: _dropoffController.text,
        fare: fare,
        distance: distance,
        estimatedMinutes: eta,
      );
      if (mounted) context.go('/ride/track/$rideId');
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    } finally {
      if (mounted) setState(() => _isBooking = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final service = ref.read(rideServiceProvider);
    final estimatedFare = service.calculateFare(_selectedVehicle, 8.0);

    return Scaffold(
      appBar: AppBar(title: const Text('Book a Ride')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _pickupController,
              decoration: InputDecoration(
                labelText: 'Pickup Location',
                prefixIcon: Icon(Icons.my_location, color: AppColors.success),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _dropoffController,
              decoration: const InputDecoration(
                labelText: 'Drop-off Location',
                prefixIcon: Icon(Icons.location_on, color: AppColors.error),
              ),
            ),
            const SizedBox(height: 24),
            Text('Vehicle Type', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            ...['car', 'bike', 'taxi'].map((type) {
              final icons = {'car': Icons.directions_car, 'bike': Icons.two_wheeler, 'taxi': Icons.local_taxi};
              final labels = {'car': 'Car', 'bike': 'Bike', 'taxi': 'Taxi'};
              return RadioListTile<String>(
                value: type,
                groupValue: _selectedVehicle,
                onChanged: (v) => setState(() => _selectedVehicle = v!),
                title: Row(
                  children: [
                    Icon(icons[type], color: AppColors.eRideColor),
                    const SizedBox(width: 8),
                    Text(labels[type]!),
                  ],
                ),
                subtitle: Text('Est. ${AppDateUtils.formatCurrency(service.calculateFare(type, 8.0))}'),
              );
            }),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.eRideColor.withOpacity(0.05),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Estimated Fare', style: TextStyle(fontSize: 16)),
                  Text(
                    AppDateUtils.formatCurrency(estimatedFare),
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.eRideColor),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            FilledButton(
              onPressed: _isBooking ? null : _bookRide,
              style: FilledButton.styleFrom(
                backgroundColor: AppColors.eRideColor,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _isBooking
                  ? const CircularProgressIndicator(strokeWidth: 2, color: Colors.white)
                  : const Text('Book Ride', style: TextStyle(fontSize: 16)),
            ),
          ],
        ),
      ),
    );
  }
}
