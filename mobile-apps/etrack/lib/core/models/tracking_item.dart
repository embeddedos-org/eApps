import 'tracking_enums.dart';
import 'tracking_event.dart';

class TrackingItem {
  final String id;
  final String trackingNumber;
  final Carrier carrier;
  final TrackingType trackingType;
  final String label;
  final TrackingStatus status;
  final String statusExplanation;
  final DateTime? estimatedDelivery;
  final List<TrackingTag> tags;
  final List<TrackingEvent> events;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? lastRefreshed;

  const TrackingItem({
    required this.id,
    required this.trackingNumber,
    required this.carrier,
    required this.trackingType,
    this.label = '',
    this.status = TrackingStatus.unknown,
    this.statusExplanation = '',
    this.estimatedDelivery,
    this.tags = const [],
    this.events = const [],
    required this.createdAt,
    required this.updatedAt,
    this.lastRefreshed,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'tracking_number': trackingNumber,
      'carrier': carrier.name,
      'tracking_type': trackingType.name,
      'label': label,
      'status': status.name,
      'status_explanation': statusExplanation,
      'estimated_delivery': estimatedDelivery?.toIso8601String(),
      'tags': tags.map((t) => t.name).join(','),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'last_refreshed': lastRefreshed?.toIso8601String(),
    };
  }

  factory TrackingItem.fromMap(Map<String, dynamic> map, {List<TrackingEvent> events = const []}) {
    return TrackingItem(
      id: map['id'] as String,
      trackingNumber: map['tracking_number'] as String,
      carrier: Carrier.values.firstWhere(
        (c) => c.name == map['carrier'],
        orElse: () => Carrier.other,
      ),
      trackingType: TrackingType.values.firstWhere(
        (t) => t.name == map['tracking_type'],
        orElse: () => TrackingType.package,
      ),
      label: map['label'] as String? ?? '',
      status: TrackingStatus.values.firstWhere(
        (s) => s.name == map['status'],
        orElse: () => TrackingStatus.unknown,
      ),
      statusExplanation: map['status_explanation'] as String? ?? '',
      estimatedDelivery: map['estimated_delivery'] != null
          ? DateTime.tryParse(map['estimated_delivery'] as String)
          : null,
      tags: (map['tags'] as String?)
              ?.split(',')
              .where((t) => t.isNotEmpty)
              .map((t) => TrackingTag.values.firstWhere(
                    (tag) => tag.name == t,
                    orElse: () => TrackingTag.important,
                  ))
              .toList() ??
          [],
      events: events,
      createdAt: DateTime.parse(map['created_at'] as String),
      updatedAt: DateTime.parse(map['updated_at'] as String),
      lastRefreshed: map['last_refreshed'] != null
          ? DateTime.tryParse(map['last_refreshed'] as String)
          : null,
    );
  }

  TrackingItem copyWith({
    String? id,
    String? trackingNumber,
    Carrier? carrier,
    TrackingType? trackingType,
    String? label,
    TrackingStatus? status,
    String? statusExplanation,
    DateTime? estimatedDelivery,
    List<TrackingTag>? tags,
    List<TrackingEvent>? events,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? lastRefreshed,
  }) {
    return TrackingItem(
      id: id ?? this.id,
      trackingNumber: trackingNumber ?? this.trackingNumber,
      carrier: carrier ?? this.carrier,
      trackingType: trackingType ?? this.trackingType,
      label: label ?? this.label,
      status: status ?? this.status,
      statusExplanation: statusExplanation ?? this.statusExplanation,
      estimatedDelivery: estimatedDelivery ?? this.estimatedDelivery,
      tags: tags ?? this.tags,
      events: events ?? this.events,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      lastRefreshed: lastRefreshed ?? this.lastRefreshed,
    );
  }
}
