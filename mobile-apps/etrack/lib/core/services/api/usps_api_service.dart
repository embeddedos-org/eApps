import 'package:dio/dio.dart';
import 'package:xml/xml.dart';
import 'package:uuid/uuid.dart';
import '../../constants/app_constants.dart';
import '../../models/tracking_enums.dart';
import '../../models/tracking_event.dart';
import '../status_engine.dart';
import 'tracking_api_service.dart';
import 'api_config.dart';

class UspsApiService implements TrackingApiService {
  final Dio _dio = Dio();
  final StatusEngine _statusEngine = StatusEngine();
  static const _uuid = Uuid();

  @override
  Future<TrackingApiResult> fetchTracking(String trackingNumber) async {
    try {
      final userId = await ApiConfig.getUspsUserId();
      if (userId == null || userId.isEmpty) {
        return TrackingApiResult.failure('USPS API key not configured. Add it in Settings.');
      }

      final xmlRequest = '<TrackFieldRequest USERID="$userId">'
          '<TrackID ID="$trackingNumber"></TrackID>'
          '</TrackFieldRequest>';

      final response = await _dio.get(
        AppConstants.uspsApiUrl,
        queryParameters: {
          'API': 'TrackV2',
          'XML': xmlRequest,
        },
      );

      final document = XmlDocument.parse(response.data as String);
      final error = document.findAllElements('Error').firstOrNull;
      if (error != null) {
        final desc = error.findElements('Description').firstOrNull?.innerText ?? 'Unknown error';
        return TrackingApiResult.failure(desc);
      }

      final trackInfo = document.findAllElements('TrackInfo').firstOrNull;
      if (trackInfo == null) {
        return TrackingApiResult.failure('No tracking information found');
      }

      final events = <TrackingEvent>[];
      final trackDetails = trackInfo.findAllElements('TrackDetail');

      for (final detail in trackDetails) {
        final eventDate = detail.findElements('EventDate').firstOrNull?.innerText ?? '';
        final eventTime = detail.findElements('EventTime').firstOrNull?.innerText ?? '';
        final eventCity = detail.findElements('EventCity').firstOrNull?.innerText ?? '';
        final eventState = detail.findElements('EventState').firstOrNull?.innerText ?? '';
        final event = detail.findElements('Event').firstOrNull?.innerText ?? '';

        DateTime? timestamp;
        try {
          timestamp = DateTime.parse('$eventDate $eventTime'.trim());
        } catch (_) {
          timestamp = DateTime.now();
        }

        final explanation = _statusEngine.explain(event);
        final location = [eventCity, eventState].where((s) => s.isNotEmpty).join(', ');

        events.add(TrackingEvent(
          id: _uuid.v4(),
          trackingItemId: '',
          status: event,
          statusExplanation: explanation.plain,
          location: location,
          description: event,
          timestamp: timestamp,
        ));
      }

      final summary = trackInfo.findElements('TrackSummary').firstOrNull;
      if (summary != null) {
        final event = summary.findElements('Event').firstOrNull?.innerText ?? '';
        final explanation = _statusEngine.explain(event);
        final latestStatus = explanation.normalizedStatus;

        return TrackingApiResult(
          success: true,
          status: latestStatus,
          statusDescription: event,
          events: events,
          carrier: 'USPS',
        );
      }

      return TrackingApiResult(
        success: true,
        status: events.isNotEmpty
            ? _statusEngine.explain(events.first.status).normalizedStatus
            : TrackingStatus.unknown,
        events: events,
        carrier: 'USPS',
      );
    } on DioException catch (e) {
      return TrackingApiResult.failure('Network error: ${e.message}');
    } catch (e) {
      return TrackingApiResult.failure('Error: $e');
    }
  }
}
