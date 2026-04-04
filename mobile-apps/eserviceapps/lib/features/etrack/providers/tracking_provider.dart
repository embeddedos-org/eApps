import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/auth_provider.dart';
import '../models/delivery_model.dart';
import '../services/tracking_service.dart';

final trackingServiceProvider = Provider<TrackingService>((ref) => TrackingService());

final activeDeliveriesProvider = StreamProvider<List<DeliveryModel>>((ref) {
  final user = ref.watch(currentUserProvider);
  return user.when(
    data: (u) {
      if (u == null) return Stream.value([]);
      return ref.read(trackingServiceProvider).getActiveDeliveries(u.uid);
    },
    loading: () => Stream.value([]),
    error: (_, __) => Stream.value([]),
  );
});

final allDeliveriesProvider = StreamProvider<List<DeliveryModel>>((ref) {
  final user = ref.watch(currentUserProvider);
  return user.when(
    data: (u) {
      if (u == null) return Stream.value([]);
      return ref.read(trackingServiceProvider).getAllDeliveries(u.uid);
    },
    loading: () => Stream.value([]),
    error: (_, __) => Stream.value([]),
  );
});

final deliveryDetailProvider =
    StreamProvider.family<DeliveryModel?, String>((ref, deliveryId) {
  return ref.watch(trackingServiceProvider).watchDelivery(deliveryId);
});
