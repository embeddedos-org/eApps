import '../models/tracking_enums.dart';

class EtaPrediction {
  final DateTime? estimatedDate;
  final String confidence;
  final DateTime? rangeMin;
  final DateTime? rangeMax;
  final String description;

  const EtaPrediction({
    this.estimatedDate,
    this.confidence = 'low',
    this.rangeMin,
    this.rangeMax,
    this.description = '',
  });
}

class EtaPredictor {
  EtaPrediction predict(Carrier carrier, TrackingStatus status, DateTime? firstEventDate) {
    final now = DateTime.now();
    final baseDate = firstEventDate ?? now;

    if (status == TrackingStatus.delivered) {
      return const EtaPrediction(
        confidence: 'high',
        description: 'Already delivered',
      );
    }

    if (status == TrackingStatus.failed || status == TrackingStatus.returned) {
      return const EtaPrediction(
        confidence: 'none',
        description: 'Delivery unsuccessful',
      );
    }

    if (carrier == Carrier.uscis) {
      return _predictUSCIS(status, baseDate);
    }

    if (carrier == Carrier.airline) {
      return const EtaPrediction(
        confidence: 'high',
        description: 'Check airline for real-time flight status',
      );
    }

    return _predictPackage(carrier, status, baseDate);
  }

  EtaPrediction _predictPackage(Carrier carrier, TrackingStatus status, DateTime baseDate) {
    int minDays, maxDays;

    switch (status) {
      case TrackingStatus.outForDelivery:
        return EtaPrediction(
          estimatedDate: DateTime.now(),
          confidence: 'high',
          rangeMin: DateTime.now(),
          rangeMax: DateTime.now(),
          description: 'Expected today',
        );
      case TrackingStatus.inTransit:
        switch (carrier) {
          case Carrier.ups:
          case Carrier.fedex:
            minDays = 1;
            maxDays = 3;
          case Carrier.usps:
            minDays = 1;
            maxDays = 5;
          case Carrier.dhl:
            minDays = 2;
            maxDays = 7;
          default:
            minDays = 2;
            maxDays = 10;
        }
      case TrackingStatus.preTransit:
      case TrackingStatus.pending:
        switch (carrier) {
          case Carrier.ups:
          case Carrier.fedex:
            minDays = 2;
            maxDays = 5;
          case Carrier.usps:
            minDays = 3;
            maxDays = 7;
          default:
            minDays = 3;
            maxDays = 14;
        }
      case TrackingStatus.delayed:
        minDays = 2;
        maxDays = 7;
      default:
        minDays = 3;
        maxDays = 10;
    }

    final now = DateTime.now();
    final estimatedMin = now.add(Duration(days: minDays));
    final estimatedMax = now.add(Duration(days: maxDays));
    final estimated = now.add(Duration(days: (minDays + maxDays) ~/ 2));

    return EtaPrediction(
      estimatedDate: estimated,
      confidence: (maxDays - minDays) <= 2 ? 'medium' : 'low',
      rangeMin: estimatedMin,
      rangeMax: estimatedMax,
      description: 'Expected in $minDays–$maxDays business days',
    );
  }

  EtaPrediction _predictUSCIS(TrackingStatus status, DateTime baseDate) {
    switch (status) {
      case TrackingStatus.pending:
        return const EtaPrediction(
          confidence: 'low',
          description: 'USCIS processing times vary (weeks to months)',
        );
      case TrackingStatus.inTransit:
        return const EtaPrediction(
          confidence: 'low',
          description: 'Case is being processed — check USCIS for estimated times',
        );
      case TrackingStatus.outForDelivery:
        return EtaPrediction(
          estimatedDate: DateTime.now().add(const Duration(days: 5)),
          confidence: 'medium',
          description: 'Card mailed — typically arrives in 5–7 business days',
        );
      default:
        return const EtaPrediction(
          confidence: 'low',
          description: 'Check USCIS website for processing times',
        );
    }
  }
}
