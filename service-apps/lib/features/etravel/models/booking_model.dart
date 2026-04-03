import 'package:cloud_firestore/cloud_firestore.dart';

class BookingModel {
  final String id;
  final String userId;
  final BookingType type;
  final String origin;
  final String destination;
  final DateTime travelDate;
  final BookingStatus status;
  final double price;
  final String details;
  final DateTime createdAt;

  const BookingModel({
    required this.id,
    required this.userId,
    required this.type,
    required this.origin,
    required this.destination,
    required this.travelDate,
    this.status = BookingStatus.confirmed,
    required this.price,
    this.details = '',
    required this.createdAt,
  });

  factory BookingModel.fromMap(Map<String, dynamic> map, String id) {
    return BookingModel(
      id: id,
      userId: map['userId'] ?? '',
      type: BookingType.values.firstWhere(
        (e) => e.name == map['type'],
        orElse: () => BookingType.ride,
      ),
      origin: map['origin'] ?? '',
      destination: map['destination'] ?? '',
      travelDate: (map['travelDate'] as Timestamp?)?.toDate() ?? DateTime.now(),
      status: BookingStatus.values.firstWhere(
        (e) => e.name == map['status'],
        orElse: () => BookingStatus.confirmed,
      ),
      price: (map['price'] ?? 0).toDouble(),
      details: map['details'] ?? '',
      createdAt: (map['createdAt'] as Timestamp?)?.toDate() ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'userId': userId,
      'type': type.name,
      'origin': origin,
      'destination': destination,
      'travelDate': Timestamp.fromDate(travelDate),
      'status': status.name,
      'price': price,
      'details': details,
      'createdAt': FieldValue.serverTimestamp(),
    };
  }
}

enum BookingType { ride, bus, train, metro, accommodation, tour }
enum BookingStatus { pending, confirmed, inProgress, completed, cancelled }
