class TrackingEvent {
  final String id;
  final String trackingItemId;
  final String status;
  final String statusExplanation;
  final String location;
  final String description;
  final DateTime timestamp;

  const TrackingEvent({
    required this.id,
    required this.trackingItemId,
    required this.status,
    this.statusExplanation = '',
    this.location = '',
    this.description = '',
    required this.timestamp,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'tracking_item_id': trackingItemId,
      'status': status,
      'status_explanation': statusExplanation,
      'location': location,
      'description': description,
      'timestamp': timestamp.toIso8601String(),
    };
  }

  factory TrackingEvent.fromMap(Map<String, dynamic> map) {
    return TrackingEvent(
      id: map['id'] as String,
      trackingItemId: map['tracking_item_id'] as String,
      status: map['status'] as String,
      statusExplanation: map['status_explanation'] as String? ?? '',
      location: map['location'] as String? ?? '',
      description: map['description'] as String? ?? '',
      timestamp: DateTime.parse(map['timestamp'] as String),
    );
  }

  TrackingEvent copyWith({
    String? id,
    String? trackingItemId,
    String? status,
    String? statusExplanation,
    String? location,
    String? description,
    DateTime? timestamp,
  }) {
    return TrackingEvent(
      id: id ?? this.id,
      trackingItemId: trackingItemId ?? this.trackingItemId,
      status: status ?? this.status,
      statusExplanation: statusExplanation ?? this.statusExplanation,
      location: location ?? this.location,
      description: description ?? this.description,
      timestamp: timestamp ?? this.timestamp,
    );
  }
}
