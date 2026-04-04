import '../../models/tracking_enums.dart';
import 'tracking_api_service.dart';
import 'usps_api_service.dart';
import 'fedex_api_service.dart';
import 'ups_api_service.dart';
import 'flight_api_service.dart';

class TrackingApiOrchestrator {
  final _usps = UspsApiService();
  final _fedex = FedexApiService();
  final _ups = UpsApiService();
  final _flight = FlightApiService();

  Future<TrackingApiResult> fetchTracking(
      String trackingNumber, Carrier carrier) async {
    switch (carrier) {
      case Carrier.usps:
        return _usps.fetchTracking(trackingNumber);
      case Carrier.fedex:
        return _fedex.fetchTracking(trackingNumber);
      case Carrier.ups:
        return _ups.fetchTracking(trackingNumber);
      case Carrier.airline:
        return _flight.fetchTracking(trackingNumber);
      default:
        return TrackingApiResult.failure(
            'No API integration available for ${carrier.label}. '
            'You can still track manually.');
    }
  }
}
