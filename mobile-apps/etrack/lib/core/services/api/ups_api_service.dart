import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:uuid/uuid.dart';
import '../../constants/app_constants.dart';
import '../../models/tracking_enums.dart';
import '../../models/tracking_event.dart';
import '../status_engine.dart';
import 'tracking_api_service.dart';
import 'api_config.dart';

class UpsApiService implements TrackingApiService {
  final Dio _dio = Dio();
  final StatusEngine _statusEngine = StatusEngine();
  static const _uuid = Uuid();
  String? _accessToken;
  DateTime? _tokenExpiry;

  Future<String?> _getAccessToken() async {
    if (_accessToken != null &&
        _tokenExpiry != null &&
        DateTime.now().isBefore(_tokenExpiry!)) {
      return _accessToken;
    }

    final clientId = await ApiConfig.getUpsClientId();
    final clientSecret = await ApiConfig.getUpsClientSecret();
    if (clientId == null || clientId.isEmpty ||
        clientSecret == null || clientSecret.isEmpty) {
      return null;
    }

    try {
      final credentials = base64Encode(utf8.encode('$clientId:$clientSecret'));
      final response = await _dio.post(
        AppConstants.upsAuthUrl,
        data: 'grant_type=client_credentials',
        options: Options(
          contentType: Headers.formUrlEncodedContentType,
          headers: {'Authorization': 'Basic $credentials'},
        ),
      );
      _accessToken = response.data['access_token'] as String;
      final expiresIn = response.data['expires_in'] as int? ?? 3600;
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
        return TrackingApiResult.failure(
            'UPS API keys not configured. Add them in Settings.');
      }

      final response = await _dio.get(
        '${AppConstants.upsTrackUrl}/$trackingNumber',
        queryParameters: {'locale': 'en_US', 'returnSignature': 'false'},
        options: Options(headers: {
          'Authorization': 'Bearer $token',
          'transId': _uuid.v4(),
          'transactionSrc': 'eTrack',
        }),
      );

      final data = response.data as Map<String, dynamic>;
      final shipments =
          data['trackResponse']?['shipment'] as List? ?? [];
      if (shipments.isEmpty) {
        return TrackingApiResult.failure('No tracking results found');
      }

      final packages =
          (shipments.first as Map<String, dynamic>)['package'] as List? ?? [];
      if (packages.isEmpty) {
        return TrackingApiResult.failure('No package data available');
      }

      final pkg = packages.first as Map<String, dynamic>;
      final activities = pkg['activity'] as List? ?? [];
      final events = <TrackingEvent>[];

      for (final activity in activities) {
        final statusDesc =
            activity['status']?['description'] as String? ?? '';
        final city =
            activity['location']?['address']?['city'] as String? ?? '';
        final state = activity['location']?['address']?['stateProvince']
                as String? ?? '';
        final dateStr = activity['date'] as String? ?? '';
        final timeStr = activity['time'] as String? ?? '';

        DateTime timestamp = DateTime.now();
        try {
          if (dateStr.length == 8 && timeStr.length >= 4) {
            timestamp = DateTime.parse(
              '${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-'
              '${dateStr.substring(6, 8)}T${timeStr.substring(0, 2)}:'
              '${timeStr.substring(2, 4)}:00',
            );
          }
        } catch (_) {}

        final explanation = _statusEngine.explain(statusDesc);
        final location =
            [city, state].where((s) => s.isNotEmpty).join(', ');

        events.add(TrackingEvent(
          id: _uuid.v4(),
          trackingItemId: '',
          status: statusDesc,
          statusExplanation: explanation.plain,
          location: location,
          description: statusDesc,
          timestamp: timestamp,
        ));
      }

      final currentStatus =
          pkg['currentStatus']?['description'] as String? ?? '';
      final explanation = _statusEngine.explain(
          currentStatus.isNotEmpty
              ? currentStatus
              : (events.isNotEmpty ? events.first.status : ''));

      return TrackingApiResult(
        success: true,
        status: explanation.normalizedStatus,
        statusDescription:
            currentStatus.isNotEmpty ? currentStatus : explanation.plain,
        events: events,
        carrier: 'UPS',
      );
    } on DioException catch (e) {
      return TrackingApiResult.failure('Network error: ${e.message}');
    } catch (e) {
      return TrackingApiResult.failure('Error: $e');
    }
  }
}
