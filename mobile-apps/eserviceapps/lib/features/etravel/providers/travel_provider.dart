import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/auth_provider.dart';
import '../models/booking_model.dart';
import '../services/travel_service.dart';

final travelServiceProvider = Provider<TravelService>((ref) => TravelService());

final userBookingsProvider = StreamProvider<List<BookingModel>>((ref) {
  final user = ref.watch(currentUserProvider);
  return user.when(
    data: (u) {
      if (u == null) return Stream.value([]);
      return ref.read(travelServiceProvider).getUserBookings(u.uid);
    },
    loading: () => Stream.value([]),
    error: (_, __) => Stream.value([]),
  );
});

final bookingDetailProvider = FutureProvider.family<BookingModel, String>((
  ref,
  bookingId,
) {
  return ref.read(travelServiceProvider).getBooking(bookingId);
});
