import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:uuid/uuid.dart';
import '../../constants/app_constants.dart';
import '../../models/tracking_enums.dart';
import '../../models/tracking_event.dart';
import '../status_engine.dart';
import 'tracking_api_service.dart';
import 'api_config.dart';

class FedexApiService implements TrackingApiService {
  final Dio _dio = Dio();
  final StatusEngine _statusEngine = StatusEngine();
  static const _uuid = Uuid();
  String? _accessToken;
  DateTime? _tokenExpiry;

  Future<String?> _getAccessToken() async {
    if (_accessToken != null && _tokenExpiry != null && DateTime.now().isBefore(_tokenExpiry!)) {
      return _accessToken;
    }

    final clientId = await ApiConfig.getFedexClientId();
    final clientSecret = await ApiConfig.getFedexClientSecret();

    if (clientId == null || clientId.isEmpty || clientSecret == null || clientSecret.isEmpty) {
      return null;
    }

    try {
      final response = await _dio.post(
        AppConstants.fedexAuthUrl,
        data: {
          'grant_type': 'client_credentials',
          'client_id': clientId,
          'client_secret': clientSecret,
        },
        options: Options(contentType: Headers.formUrlEncodedContentType),
      );

      _accessToken = response.data['access_token'] as String;
      final expiresIn = response.data['expires_in'] as int;
      _tokenExpiry = DateTime.now().add(Duration(seconds: expiresIn - 60));
      return _accessToken;
    } catch (_) {
      return null;
    }
  }

  @override
  Future<TrackingApiResult> fetchTracking(String trackingNumber) async {
    try {
      final token = await _getAccessToken();
      if (token == null) {
        return TrackingApiResult.failure('FedEx API keys not configured. Add them in Settings.');
      }

      final response = await _dio.post(
        AppConstants.fedexTrackUrl,
        data: jsonEncode({
          'trackingInfo': [
            {
              'trackingNumberInfo': {
                'trackingNumber': trackingNumber,
              }
            }
          ],
          'includeDetailedScans': true,
        }),
        options: Options(headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        }),
      );

      final data = response.data as Map<String, dynamic>;
      final results = data['output']?['completeTrackResults'] as List?;
      if (results == null || results.isEmpty) {
        return TrackingApiResult.failure('No tracking results found');
      }

      final trackResult = results.first['trackResults']?.first as Map<String, dynamic>?;
      if (trackResult == null) {
        return TrackingApiResult.failure('No tracking data available');
      }

      final events = <TrackingEvent>[];
      final scanEvents = trackResult['scanEvents'] as List? ?? [];

      for (final scan in scanEvents) {
        final date = scan['date'] as String? ?? '';
        final eventDesc = scan['eventDescription'] as String? ?? '';
        final city = scan['scanLocation']?['city'] as String? ?? '';
        final state = scan['scanLocation']?['stateOrProvinceCode'] as String? ?? '';

        DateTime? timestamp;
        try {
          timestamp = DateTime.parse(date);
        } catch (_) {
          timestamp = DateTime.now();
        }

        final explanation = _statusEngine.explain(eventDesc);
        final location = [city, state].where((s) => s.isNotEmpty).join(', ');

        events.add(TrackingEvent(
          id: _uuid.v4(),
          trackingItemId: '',
          status: eventDesc,
          statusExplanation: explanation.plain,
          location: location,
          description: eventDesc,
          timestamp: timestamp,
        ));
      }

      final latestStatus = trackResult['latestStatusDetail']?['description'] as String? ?? '';
      final explanation = _statusEngine.explain(latestStatus);

      final etaStr = trackResult['estimatedDeliveryTimeWindow']?['window']?['ends'] as String?;
      DateTime? eta;
      if (etaStr != null) {
        try {
          eta = DateTime.parse(etaStr);
        } catch (_) {}
      }

      return TrackingApiResult(
        success: true,
        status: explanation.normalizedStatus,
        statusDescription: latestStatus,
        events: events,
        estimatedDelivery: eta,
        carrier: 'FedEx',
      );
    } on DioException catch (e) {
      return TrackingApiResult.failure('Network error: ${e.message}');
    } catch (e) {
      return TrackingApiResult.failure('Error: $e');
    }
  }
}
