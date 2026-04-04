import '../../models/tracking_enums.dart';
import '../../models/tracking_event.dart';

class TrackingApiResult {
  final bool success;
  final String? error;
  final TrackingStatus status;
  final String statusDescription;
  final List<TrackingEvent> events;
  final DateTime? estimatedDelivery;
  final String carrier;

  const TrackingApiResult({
    required this.success,
    this.error,
    this.status = TrackingStatus.unknown,
    this.statusDescription = '',
    this.events = const [],
    this.estimatedDelivery,
    this.carrier = '',
  });

  factory TrackingApiResult.failure(String error) {
    return TrackingApiResult(success: false, error: error);
  }
}

abstract class TrackingApiService {
  Future<TrackingApiResult> fetchTracking(String trackingNumber);
}
