import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/auth_provider.dart';
import '../models/ride_model.dart';
import '../services/ride_service.dart';

final rideServiceProvider = Provider<RideService>((ref) => RideService());

final activeRideProvider = StreamProvider<RideModel?>((ref) {
  final authState = ref.watch(authStateProvider);
  final rideService = ref.watch(rideServiceProvider);

  final user = authState.valueOrNull;
  if (user == null) return Stream.value(null);

  return rideService.getActiveRideForPassenger(user.uid);
});

final rideHistoryProvider = StreamProvider<List<RideModel>>((ref) {
  final authState = ref.watch(authStateProvider);
  final rideService = ref.watch(rideServiceProvider);

  final user = authState.valueOrNull;
  if (user == null) return Stream.value([]);

  return rideService.getRideHistory(user.uid);
});

final availableRidesProvider = StreamProvider<List<RideModel>>((ref) {
  final rideService = ref.watch(rideServiceProvider);
  return rideService.getAvailableRidesForDriver();
});

final driverActiveRidesProvider =
    StreamProvider.family<List<RideModel>, String>((ref, driverId) {
  final rideService = ref.watch(rideServiceProvider);
  return rideService.getDriverActiveRides(driverId);
});

final driverRideHistoryProvider =
    StreamProvider.family<List<RideModel>, String>((ref, driverId) {
  final rideService = ref.watch(rideServiceProvider);
  return rideService.getDriverRideHistory(driverId);
});

final rideStreamProvider =
    StreamProvider.family<RideModel?, String>((ref, rideId) {
  final rideService = ref.watch(rideServiceProvider);
  return rideService.getRideStream(rideId);
});

final nearbyDriversProvider =
    Provider.family<List<Map<String, dynamic>>, ({double lat, double lng})>(
        (ref, coords) {
  final rideService = ref.watch(rideServiceProvider);
  return rideService.getNearbyDrivers(coords.lat, coords.lng);
});

final fareEstimateProvider = Provider.family<double,
    ({double distance, int duration, String vehicleType})>((ref, params) {
  final rideService = ref.watch(rideServiceProvider);
  return rideService.calculateFare(
      params.distance, params.duration, params.vehicleType);
});
