import '../models/tracking_enums.dart';

class StatusExplanation {
  final String plain;
  final String emoji;
  final TrackingStatus normalizedStatus;

  const StatusExplanation({
    required this.plain,
    required this.emoji,
    required this.normalizedStatus,
  });
}

class StatusEngine {
  static const _statusMap = <String, StatusExplanation>{
    // USPS statuses
    'DELIVERED': StatusExplanation(
      plain: 'Your package has been delivered',
      emoji: '✅',
      normalizedStatus: TrackingStatus.delivered,
    ),
    'DELIVERED, IN/AT MAILBOX': StatusExplanation(
      plain: 'Your package was delivered to your mailbox',
      emoji: '📬',
      normalizedStatus: TrackingStatus.delivered,
    ),
    'DELIVERED, FRONT DOOR': StatusExplanation(
      plain: 'Your package was left at your front door',
      emoji: '🚪',
      normalizedStatus: TrackingStatus.delivered,
    ),
    'OUT FOR DELIVERY': StatusExplanation(
      plain: 'Your package is on the delivery truck and will arrive today',
      emoji: '🚚',
      normalizedStatus: TrackingStatus.outForDelivery,
    ),
    'IN TRANSIT TO NEXT FACILITY': StatusExplanation(
      plain: 'Your package is moving between sorting centers',
      emoji: '🔄',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'IN TRANSIT': StatusExplanation(
      plain: 'Your package is on its way',
      emoji: '🚚',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'ARRIVED AT FACILITY': StatusExplanation(
      plain: 'Your package arrived at a processing facility',
      emoji: '🏭',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'ARRIVED AT POST OFFICE': StatusExplanation(
      plain: 'Your package arrived at your local post office',
      emoji: '🏤',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'ARRIVAL AT UNIT': StatusExplanation(
      plain: 'Your package arrived at your local post office',
      emoji: '📬',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'DEPARTED FACILITY': StatusExplanation(
      plain: 'Your package left a processing facility',
      emoji: '📤',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'ACCEPTED AT USPS ORIGIN FACILITY': StatusExplanation(
      plain: 'USPS has received your package and it entered the mail system',
      emoji: '📥',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'SHIPPING LABEL CREATED': StatusExplanation(
      plain: 'A shipping label was created but the package hasn\'t been picked up yet',
      emoji: '🏷️',
      normalizedStatus: TrackingStatus.preTransit,
    ),
    'PRE-SHIPMENT': StatusExplanation(
      plain: 'The sender has prepared the shipment but it hasn\'t entered the mail system yet',
      emoji: '📝',
      normalizedStatus: TrackingStatus.preTransit,
    ),
    'AVAILABLE FOR PICKUP': StatusExplanation(
      plain: 'Your package is ready for pickup at the post office',
      emoji: '📬',
      normalizedStatus: TrackingStatus.availableForPickup,
    ),
    'DELIVERY ATTEMPTED': StatusExplanation(
      plain: 'Delivery was attempted but no one was available to receive the package',
      emoji: '🔔',
      normalizedStatus: TrackingStatus.delayed,
    ),
    'RETURN TO SENDER': StatusExplanation(
      plain: 'The package is being returned to the sender',
      emoji: '↩️',
      normalizedStatus: TrackingStatus.returned,
    ),

    // FedEx statuses
    'PICKED UP': StatusExplanation(
      plain: 'Your package has been picked up by the carrier',
      emoji: '📦',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'ON FEDEX VEHICLE FOR DELIVERY': StatusExplanation(
      plain: 'Your package is on a FedEx truck for delivery today',
      emoji: '🚚',
      normalizedStatus: TrackingStatus.outForDelivery,
    ),
    'AT LOCAL FEDEX FACILITY': StatusExplanation(
      plain: 'Your package is at a nearby FedEx facility',
      emoji: '🏢',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'IN TRANSIT TO DESTINATION': StatusExplanation(
      plain: 'Your package is being transported to the delivery area',
      emoji: '✈️',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'DELIVERY EXCEPTION': StatusExplanation(
      plain: 'There was a problem with delivery — check details for more info',
      emoji: '⚠️',
      normalizedStatus: TrackingStatus.delayed,
    ),

    // UPS statuses
    'ON THE WAY': StatusExplanation(
      plain: 'Your package is on the way to you',
      emoji: '🚚',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'OUT FOR DELIVERY TODAY': StatusExplanation(
      plain: 'Your package is out for delivery and should arrive today',
      emoji: '📦',
      normalizedStatus: TrackingStatus.outForDelivery,
    ),
    'DESTINATION SCAN': StatusExplanation(
      plain: 'Your package was scanned at the delivery facility near you',
      emoji: '📍',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'ORIGIN SCAN': StatusExplanation(
      plain: 'Your package was scanned at the origin facility',
      emoji: '🏭',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'DEPARTURE SCAN': StatusExplanation(
      plain: 'Your package left a UPS facility',
      emoji: '📤',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'ARRIVAL SCAN': StatusExplanation(
      plain: 'Your package arrived at a UPS facility',
      emoji: '📥',
      normalizedStatus: TrackingStatus.inTransit,
    ),

    // DHL statuses
    'SHIPMENT PICKED UP': StatusExplanation(
      plain: 'DHL has picked up the shipment',
      emoji: '📦',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'CUSTOMS CLEARANCE': StatusExplanation(
      plain: 'Your package is being processed through customs',
      emoji: '🛃',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'CLEARANCE EVENT': StatusExplanation(
      plain: 'Your package is going through customs clearance',
      emoji: '🛃',
      normalizedStatus: TrackingStatus.inTransit,
    ),

    // USCIS statuses
    'CASE WAS RECEIVED': StatusExplanation(
      plain: 'USCIS has received your case and it is being processed',
      emoji: '📋',
      normalizedStatus: TrackingStatus.pending,
    ),
    'CASE IS BEING ACTIVELY REVIEWED': StatusExplanation(
      plain: 'An officer is actively reviewing your case',
      emoji: '🔍',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'CASE WAS APPROVED': StatusExplanation(
      plain: 'Your case has been approved',
      emoji: '✅',
      normalizedStatus: TrackingStatus.delivered,
    ),
    'CASE WAS DENIED': StatusExplanation(
      plain: 'Your case has been denied',
      emoji: '❌',
      normalizedStatus: TrackingStatus.failed,
    ),
    'REQUEST FOR EVIDENCE WAS SENT': StatusExplanation(
      plain: 'USCIS needs more documents — check your mail for details',
      emoji: '📨',
      normalizedStatus: TrackingStatus.delayed,
    ),
    'FINGERPRINT FEE WAS RECEIVED': StatusExplanation(
      plain: 'Your biometrics fee has been received',
      emoji: '🖐️',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'CARD IS BEING PRODUCED': StatusExplanation(
      plain: 'Your card (EAD/Green Card) is being manufactured',
      emoji: '🏭',
      normalizedStatus: TrackingStatus.inTransit,
    ),
    'CARD WAS MAILED TO ME': StatusExplanation(
      plain: 'Your card has been mailed to your address',
      emoji: '📮',
      normalizedStatus: TrackingStatus.outForDelivery,
    ),
    'CARD WAS DELIVERED': StatusExplanation(
      plain: 'Your card has been delivered',
      emoji: '✅',
      normalizedStatus: TrackingStatus.delivered,
    ),
  };

  StatusExplanation explain(String rawStatus) {
    final upper = rawStatus.toUpperCase().trim();

    if (_statusMap.containsKey(upper)) {
      return _statusMap[upper]!;
    }

    // Fuzzy matching
    for (final entry in _statusMap.entries) {
      if (upper.contains(entry.key) || entry.key.contains(upper)) {
        return entry.value;
      }
    }

    // Keyword-based fallback
    if (upper.contains('DELIVER') && !upper.contains('EXCEPTION') && !upper.contains('ATTEMPT')) {
      return const StatusExplanation(
        plain: 'Your package has been delivered',
        emoji: '✅',
        normalizedStatus: TrackingStatus.delivered,
      );
    }
    if (upper.contains('TRANSIT') || upper.contains('SHIPPED') || upper.contains('DEPARTED')) {
      return const StatusExplanation(
        plain: 'Your package is in transit',
        emoji: '🚚',
        normalizedStatus: TrackingStatus.inTransit,
      );
    }
    if (upper.contains('OUT FOR DELIVERY')) {
      return const StatusExplanation(
        plain: 'Your package is out for delivery',
        emoji: '📦',
        normalizedStatus: TrackingStatus.outForDelivery,
      );
    }
    if (upper.contains('FAIL') || upper.contains('DENIED') || upper.contains('REFUSED')) {
      return const StatusExplanation(
        plain: 'There was a problem with this shipment',
        emoji: '❌',
        normalizedStatus: TrackingStatus.failed,
      );
    }
    if (upper.contains('RETURN')) {
      return const StatusExplanation(
        plain: 'This item is being returned',
        emoji: '↩️',
        normalizedStatus: TrackingStatus.returned,
      );
    }
    if (upper.contains('DELAY') || upper.contains('EXCEPTION') || upper.contains('HOLD')) {
      return const StatusExplanation(
        plain: 'There is a delay with this shipment',
        emoji: '⚠️',
        normalizedStatus: TrackingStatus.delayed,
      );
    }
    if (upper.contains('LABEL') || upper.contains('PRE-SHIPMENT') || upper.contains('CREATED')) {
      return const StatusExplanation(
        plain: 'Shipment label created, awaiting pickup',
        emoji: '🏷️',
        normalizedStatus: TrackingStatus.preTransit,
      );
    }

    return StatusExplanation(
      plain: rawStatus,
      emoji: '❓',
      normalizedStatus: TrackingStatus.unknown,
    );
  }
}
