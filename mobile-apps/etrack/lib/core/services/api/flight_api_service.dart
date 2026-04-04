import 'package:dio/dio.dart';
import 'package:uuid/uuid.dart';
import '../../constants/app_constants.dart';
import '../../models/tracking_enums.dart';
import '../../models/tracking_event.dart';
import 'tracking_api_service.dart';
import 'api_config.dart';

class FlightApiService implements TrackingApiService {
  final Dio _dio = Dio();
  static const _uuid = Uuid();

  @override
  Future<TrackingApiResult> fetchTracking(String flightNumber) async {
    try {
      final apiKey = await ApiConfig.getAviationStackKey();
      if (apiKey == null || apiKey.isEmpty) {
        return TrackingApiResult.failure(
            'AviationStack API key not configured. Add it in Settings.');
      }

      final cleaned = flightNumber.replaceAll(RegExp(r'\s+'), '');

      final response = await _dio.get(
        AppConstants.aviationStackUrl,
        queryParameters: {
          'access_key': apiKey,
          'flight_iata': cleaned,
        },
      );

      final data = response.data as Map<String, dynamic>;
      final flights = data['data'] as List? ?? [];
      if (flights.isEmpty) {
        return TrackingApiResult.failure('No flight data found for $flightNumber');
      }

      final flight = flights.first as Map<String, dynamic>;
      final flightStatus = flight['flight_status'] as String? ?? 'unknown';
      final departure = flight['departure'] as Map<String, dynamic>? ?? {};
      final arrival = flight['arrival'] as Map<String, dynamic>? ?? {};

      final events = <TrackingEvent>[];
      final depTime = departure['actual'] ?? departure['estimated'] ?? departure['scheduled'];
      final arrTime = arrival['actual'] ?? arrival['estimated'] ?? arrival['scheduled'];

      if (depTime != null) {
        events.add(TrackingEvent(
          id: _uuid.v4(),
          trackingItemId: '',
          status: 'Departed',
          statusExplanation: 'Flight departed from ${departure['airport'] ?? 'origin'}',
          location: departure['iata'] as String? ?? '',
          description: 'Departure from ${departure['airport'] ?? departure['iata'] ?? 'origin'}',
          timestamp: DateTime.tryParse(depTime as String) ?? DateTime.now(),
        ));
      }

      if (arrTime != null) {
        final isLanded = flightStatus == 'landed' || flightStatus == 'arrived';
        events.add(TrackingEvent(
          id: _uuid.v4(),
          trackingItemId: '',
          status: isLanded ? 'Arrived' : 'Expected Arrival',
          statusExplanation: isLanded
              ? 'Flight arrived at ${arrival['airport'] ?? 'destination'}'
              : 'Expected arrival at ${arrival['airport'] ?? 'destination'}',
          location: arrival['iata'] as String? ?? '',
          description: '${isLanded ? 'Arrival' : 'Expected arrival'} at ${arrival['airport'] ?? arrival['iata'] ?? 'destination'}',
          timestamp: DateTime.tryParse(arrTime as String) ?? DateTime.now(),
        ));
      }

      TrackingStatus status;
      switch (flightStatus) {
        case 'landed':
        case 'arrived':
          status = TrackingStatus.delivered;
        case 'active':
        case 'en-route':
          status = TrackingStatus.inTransit;
        case 'scheduled':
          status = TrackingStatus.pending;
        case 'cancelled':
        case 'diverted':
          status = TrackingStatus.failed;
        case 'delayed':
          status = TrackingStatus.delayed;
        default:
          status = TrackingStatus.unknown;
      }

      return TrackingApiResult(
        success: true,
        status: status,
        statusDescription: 'Flight $flightStatus',
        events: events,
        carrier: 'Airline',
      );
    } on DioException catch (e) {
      return TrackingApiResult.failure('Network error: ${e.message}');
    } catch (e) {
      return TrackingApiResult.failure('Error: $e');
    }
  }
}
