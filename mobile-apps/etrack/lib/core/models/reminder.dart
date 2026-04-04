class Reminder {
  final String id;
  final String trackingItemId;
  final DateTime scheduledTime;
  final String message;
  final bool isActive;

  const Reminder({
    required this.id,
    required this.trackingItemId,
    required this.scheduledTime,
    this.message = '',
    this.isActive = true,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'tracking_item_id': trackingItemId,
      'scheduled_time': scheduledTime.toIso8601String(),
      'message': message,
      'is_active': isActive ? 1 : 0,
    };
  }

  factory Reminder.fromMap(Map<String, dynamic> map) {
    return Reminder(
      id: map['id'] as String,
      trackingItemId: map['tracking_item_id'] as String,
      scheduledTime: DateTime.parse(map['scheduled_time'] as String),
      message: map['message'] as String? ?? '',
      isActive: (map['is_active'] as int?) == 1,
    );
  }

  Reminder copyWith({
    String? id,
    String? trackingItemId,
    DateTime? scheduledTime,
    String? message,
    bool? isActive,
  }) {
    return Reminder(
      id: id ?? this.id,
      trackingItemId: trackingItemId ?? this.trackingItemId,
      scheduledTime: scheduledTime ?? this.scheduledTime,
      message: message ?? this.message,
      isActive: isActive ?? this.isActive,
    );
  }
}
