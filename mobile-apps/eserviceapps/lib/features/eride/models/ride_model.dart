import 'package:cloud_firestore/cloud_firestore.dart';

class RideModel {
  final String id;
  final String userId;
  final String driverId;
  final String driverName;
  final String vehicleType;
  final double pickupLat;
  final double pickupLng;
  final String pickupAddress;
  final double dropoffLat;
  final double dropoffLng;
  final String dropoffAddress;
  final RideStatus status;
  final double fare;
  final double distance;
  final int estimatedMinutes;
  final double rating;
  final DateTime createdAt;

  const RideModel({
    required this.id,
    required this.userId,
    this.driverId = '',
    this.driverName = '',
    required this.vehicleType,
    required this.pickupLat,
    required this.pickupLng,
    required this.pickupAddress,
    required this.dropoffLat,
    required this.dropoffLng,
    required this.dropoffAddress,
    this.status = RideStatus.requested,
    this.fare = 0.0,
    this.distance = 0.0,
    this.estimatedMinutes = 0,
    this.rating = 0.0,
    required this.createdAt,
  });

  factory RideModel.fromMap(Map<String, dynamic> map, String id) {
    return RideModel(
      id: id,
      userId: map['userId'] ?? '',
      driverId: map['driverId'] ?? '',
      driverName: map['driverName'] ?? '',
      vehicleType: map['vehicleType'] ?? 'car',
      pickupLat: (map['pickupLat'] ?? 0).toDouble(),
      pickupLng: (map['pickupLng'] ?? 0).toDouble(),
      pickupAddress: map['pickupAddress'] ?? '',
      dropoffLat: (map['dropoffLat'] ?? 0).toDouble(),
      dropoffLng: (map['dropoffLng'] ?? 0).toDouble(),
      dropoffAddress: map['dropoffAddress'] ?? '',
      status: RideStatus.values.firstWhere(
        (e) => e.name == map['status'],
        orElse: () => RideStatus.requested,
      ),
      fare: (map['fare'] ?? 0).toDouble(),
      distance: (map['distance'] ?? 0).toDouble(),
      estimatedMinutes: map['estimatedMinutes'] ?? 0,
      rating: (map['rating'] ?? 0).toDouble(),
      createdAt: (map['createdAt'] as Timestamp?)?.toDate() ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'userId': userId,
      'driverId': driverId,
      'driverName': driverName,
      'vehicleType': vehicleType,
      'pickupLat': pickupLat,
      'pickupLng': pickupLng,
      'pickupAddress': pickupAddress,
      'dropoffLat': dropoffLat,
      'dropoffLng': dropoffLng,
      'dropoffAddress': dropoffAddress,
      'status': status.name,
      'fare': fare,
      'distance': distance,
      'estimatedMinutes': estimatedMinutes,
      'rating': rating,
      'createdAt': FieldValue.serverTimestamp(),
    };
  }
}

enum RideStatus { requested, accepted, driverEnRoute, arrived, inProgress, completed, cancelled }
