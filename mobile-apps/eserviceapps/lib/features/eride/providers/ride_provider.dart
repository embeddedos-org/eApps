import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/auth_provider.dart';
import '../models/ride_model.dart';
import '../services/ride_service.dart';

final rideServiceProvider = Provider<RideService>((ref) => RideService());

final userRidesProvider = StreamProvider<List<RideModel>>((ref) {
  final user = ref.watch(currentUserProvider);
  return user.when(
    data: (u) {
      if (u == null) return Stream.value([]);
      return ref.read(rideServiceProvider).getUserRides(u.uid);
    },
    loading: () => Stream.value([]),
    error: (_, __) => Stream.value([]),
  );
});

final activeRideProvider = StreamProvider<RideModel?>((ref) {
  final user = ref.watch(currentUserProvider);
  return user.when(
    data: (u) {
      if (u == null) return Stream.value(null);
      return ref.read(rideServiceProvider).getActiveRide(u.uid);
    },
    loading: () => Stream.value(null),
    error: (_, __) => Stream.value(null),
  );
});

final rideDetailProvider = StreamProvider.family<RideModel?, String>((
  ref,
  rideId,
) {
  return ref.watch(rideServiceProvider).getRide(rideId);
});
