import '../models/tracking_enums.dart';

class CarrierDetectionResult {
  final Carrier carrier;
  final TrackingType trackingType;
  final double confidence;

  const CarrierDetectionResult({
    required this.carrier,
    required this.trackingType,
    required this.confidence,
  });
}

class CarrierDetector {
  static final _uspsPatterns = [
    RegExp(r'^9[234]\d{20,24}$'),
    RegExp(r'^[0-9]{20,22}$'),
    RegExp(r'^(70|13|23)\d{18,20}$'),
    RegExp(r'^(EA|EC|CP|RA|RB)\d{9}US$', caseSensitive: false),
  ];

  static final _upsPattern = RegExp(r'^1Z[A-Z0-9]{16}$', caseSensitive: false);

  static final _fedexPatterns = [
    RegExp(r'^\d{12}$'),
    RegExp(r'^\d{15}$'),
    RegExp(r'^\d{20,22}$'),
    RegExp(r'^(96|98)\d{18,22}$'),
  ];

  static final _dhlPatterns = [
    RegExp(r'^\d{10}$'),
    RegExp(r'^JJD\d{18,}$', caseSensitive: false),
    RegExp(r'^\d{10,11}$'),
  ];

  static final _uscisPatterns = [
    RegExp(r'^(IOE|EAC|WAC|LIN|SRC|MSC|NBC|YSC)\d{10}$', caseSensitive: false),
    RegExp(r'^[A-Z]{3}\d{10}$', caseSensitive: false),
  ];

  static final _flightPattern = RegExp(
    r'^([A-Z]{2}|[A-Z]\d|\d[A-Z])\s?\d{1,4}$',
    caseSensitive: false,
  );

  CarrierDetectionResult detect(String trackingNumber) {
    final cleaned = trackingNumber.trim().toUpperCase().replaceAll(RegExp(r'\s+'), '');

    if (_upsPattern.hasMatch(cleaned)) {
      return const CarrierDetectionResult(
        carrier: Carrier.ups,
        trackingType: TrackingType.package,
        confidence: 0.95,
      );
    }

    for (final pattern in _uscisPatterns) {
      if (pattern.hasMatch(cleaned)) {
        return const CarrierDetectionResult(
          carrier: Carrier.uscis,
          trackingType: TrackingType.immigrationCase,
          confidence: 0.90,
        );
      }
    }

    if (_flightPattern.hasMatch(trackingNumber.trim())) {
      return const CarrierDetectionResult(
        carrier: Carrier.airline,
        trackingType: TrackingType.flight,
        confidence: 0.70,
      );
    }

    for (final pattern in _uspsPatterns) {
      if (pattern.hasMatch(cleaned)) {
        return const CarrierDetectionResult(
          carrier: Carrier.usps,
          trackingType: TrackingType.package,
          confidence: 0.85,
        );
      }
    }

    for (final pattern in _fedexPatterns) {
      if (pattern.hasMatch(cleaned)) {
        final isFedexSpecific = cleaned.length == 12 || cleaned.length == 15 ||
            cleaned.startsWith('96') || cleaned.startsWith('98');
        return CarrierDetectionResult(
          carrier: Carrier.fedex,
          trackingType: TrackingType.package,
          confidence: isFedexSpecific ? 0.85 : 0.60,
        );
      }
    }

    for (final pattern in _dhlPatterns) {
      if (pattern.hasMatch(cleaned)) {
        return CarrierDetectionResult(
          carrier: Carrier.dhl,
          trackingType: TrackingType.package,
          confidence: cleaned.startsWith('JJD') ? 0.90 : 0.50,
        );
      }
    }

    return const CarrierDetectionResult(
      carrier: Carrier.other,
      trackingType: TrackingType.package,
      confidence: 0.0,
    );
  }
}
