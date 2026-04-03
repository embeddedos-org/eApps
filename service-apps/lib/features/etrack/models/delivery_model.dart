import 'package:cloud_firestore/cloud_firestore.dart';

class DeliveryModel {
  final String id;
  final String userId;
  final String trackingNumber;
  final String carrier;
  final DeliveryType type;
  final DeliveryStatus status;
  final String description;
  final String estimatedDelivery;
  final List<TrackingEvent> events;
  final DateTime createdAt;

  const DeliveryModel({
    required this.id,
    required this.userId,
    required this.trackingNumber,
    required this.carrier,
    this.type = DeliveryType.parcel,
    this.status = DeliveryStatus.pending,
    this.description = '',
    this.estimatedDelivery = '',
    this.events = const [],
    required this.createdAt,
  });

  factory DeliveryModel.fromMap(Map<String, dynamic> map, String id) {
    return DeliveryModel(
      id: id,
      userId: map['userId'] ?? '',
      trackingNumber: map['trackingNumber'] ?? '',
      carrier: map['carrier'] ?? '',
      type: DeliveryType.values.firstWhere(
        (e) => e.name == map['type'],
        orElse: () => DeliveryType.parcel,
      ),
      status: DeliveryStatus.values.firstWhere(
        (e) => e.name == map['status'],
        orElse: () => DeliveryStatus.pending,
      ),
      description: map['description'] ?? '',
      estimatedDelivery: map['estimatedDelivery'] ?? '',
      events: (map['events'] as List<dynamic>?)
              ?.map((e) => TrackingEvent.fromMap(e as Map<String, dynamic>))
              .toList() ??
          [],
      createdAt: (map['createdAt'] as Timestamp?)?.toDate() ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'userId': userId,
      'trackingNumber': trackingNumber,
      'carrier': carrier,
      'type': type.name,
      'status': status.name,
      'description': description,
      'estimatedDelivery': estimatedDelivery,
      'events': events.map((e) => e.toMap()).toList(),
      'createdAt': FieldValue.serverTimestamp(),
    };
  }
}

class TrackingEvent {
  final String status;
  final String location;
  final String description;
  final DateTime timestamp;

  const TrackingEvent({
    required this.status,
    required this.location,
    required this.description,
    required this.timestamp,
  });

  factory TrackingEvent.fromMap(Map<String, dynamic> map) {
    return TrackingEvent(
      status: map['status'] ?? '',
      location: map['location'] ?? '',
      description: map['description'] ?? '',
      timestamp: (map['timestamp'] as Timestamp?)?.toDate() ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'status': status,
      'location': location,
      'description': description,
      'timestamp': Timestamp.fromDate(timestamp),
    };
  }
}

enum DeliveryType { food, parcel, grocery, courier }
enum DeliveryStatus { pending, pickedUp, inTransit, outForDelivery, delivered, failed }
