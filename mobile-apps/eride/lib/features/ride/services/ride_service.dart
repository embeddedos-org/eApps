import 'dart:math';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:uuid/uuid.dart';
import '../../../core/constants/app_constants.dart';
import '../models/ride_model.dart';

class RideService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final Uuid _uuid = const Uuid();

  Future<RideModel> requestRide({
    required String passengerId,
    required String pickupAddress,
    required String dropoffAddress,
    required double pickupLat,
    required double pickupLng,
    required double dropoffLat,
    required double dropoffLng,
    String vehicleType = 'economy',
  }) async {
    final distance = _calculateDistance(pickupLat, pickupLng, dropoffLat, dropoffLng);
    final duration = _estimateDuration(distance);
    final fare = calculateFare(distance, duration, vehicleType);

    final rideId = _uuid.v4();
    final ride = RideModel(
      id: rideId,
      passengerId: passengerId,
      pickupAddress: pickupAddress,
      dropoffAddress: dropoffAddress,
      pickupLat: pickupLat,
      pickupLng: pickupLng,
      dropoffLat: dropoffLat,
      dropoffLng: dropoffLng,
      status: RideStatus.requested,
      fare: fare,
      distance: distance,
      duration: duration,
      vehicleType: vehicleType,
      createdAt: DateTime.now(),
    );

    await _firestore
        .collection(AppConstants.ridesCollection)
        .doc(rideId)
        .set(ride.toMap());

    return ride;
  }

  Future<void> acceptRide({
    required String rideId,
    required String driverId,
    required String driverName,
    String? driverPhoto,
    String? vehiclePlate,
    String? vehicleModel,
  }) async {
    await _firestore.collection(AppConstants.ridesCollection).doc(rideId).update({
      'status': RideStatus.accepted.name,
      'driverId': driverId,
      'driverName': driverName,
      'driverPhoto': driverPhoto,
      'vehiclePlate': vehiclePlate,
      'vehicleModel': vehicleModel,
    });
  }

  Future<void> updateRideStatus(String rideId, RideStatus status) async {
    final updates = <String, dynamic>{'status': status.name};
    if (status == RideStatus.completed) {
      updates['completedAt'] = Timestamp.now();
    }
    await _firestore
        .collection(AppConstants.ridesCollection)
        .doc(rideId)
        .update(updates);
  }

  Future<void> cancelRide(String rideId, {String? reason}) async {
    await _firestore.collection(AppConstants.ridesCollection).doc(rideId).update({
      'status': RideStatus.cancelled.name,
      'cancellationReason': reason ?? 'Cancelled by user',
      'completedAt': Timestamp.now(),
    });
  }

  Future<void> rateRide(String rideId, double rating, {bool isDriver = false}) async {
    final field = isDriver ? 'passengerRating' : 'driverRating';
    await _firestore
        .collection(AppConstants.ridesCollection)
        .doc(rideId)
        .update({field: rating});
  }

  Stream<RideModel?> getRideStream(String rideId) {
    return _firestore
        .collection(AppConstants.ridesCollection)
        .doc(rideId)
        .snapshots()
        .map((doc) {
      if (!doc.exists) return null;
      return RideModel.fromMap(doc.data()!, doc.id);
    });
  }

  Stream<RideModel?> getActiveRideForPassenger(String passengerId) {
    return _firestore
        .collection(AppConstants.ridesCollection)
        .where('passengerId', isEqualTo: passengerId)
        .where('status', whereIn: [
          RideStatus.requested.name,
          RideStatus.accepted.name,
          RideStatus.arriving.name,
          RideStatus.inProgress.name,
        ])
        .orderBy('createdAt', descending: true)
        .limit(1)
        .snapshots()
        .map((snapshot) {
          if (snapshot.docs.isEmpty) return null;
          return RideModel.fromMap(snapshot.docs.first.data(), snapshot.docs.first.id);
        });
  }

  Stream<List<RideModel>> getAvailableRidesForDriver() {
    return _firestore
        .collection(AppConstants.ridesCollection)
        .where('status', isEqualTo: RideStatus.requested.name)
        .orderBy('createdAt', descending: true)
        .limit(20)
        .snapshots()
        .map((snapshot) => snapshot.docs
            .map((doc) => RideModel.fromMap(doc.data(), doc.id))
            .toList());
  }

  Stream<List<RideModel>> getDriverActiveRides(String driverId) {
    return _firestore
        .collection(AppConstants.ridesCollection)
        .where('driverId', isEqualTo: driverId)
        .where('status', whereIn: [
          RideStatus.accepted.name,
          RideStatus.arriving.name,
          RideStatus.inProgress.name,
        ])
        .snapshots()
        .map((snapshot) => snapshot.docs
            .map((doc) => RideModel.fromMap(doc.data(), doc.id))
            .toList());
  }

  Stream<List<RideModel>> getRideHistory(String userId, {int limit = 50}) {
    return _firestore
        .collection(AppConstants.ridesCollection)
        .where('passengerId', isEqualTo: userId)
        .where('status', whereIn: [RideStatus.completed.name, RideStatus.cancelled.name])
        .orderBy('createdAt', descending: true)
        .limit(limit)
        .snapshots()
        .map((snapshot) => snapshot.docs
            .map((doc) => RideModel.fromMap(doc.data(), doc.id))
            .toList());
  }

  Stream<List<RideModel>> getDriverRideHistory(String driverId, {int limit = 50}) {
    return _firestore
        .collection(AppConstants.ridesCollection)
        .where('driverId', isEqualTo: driverId)
        .where('status', isEqualTo: RideStatus.completed.name)
        .orderBy('createdAt', descending: true)
        .limit(limit)
        .snapshots()
        .map((snapshot) => snapshot.docs
            .map((doc) => RideModel.fromMap(doc.data(), doc.id))
            .toList());
  }

  double calculateFare(double distanceKm, int durationMinutes, String vehicleType) {
    final multiplier = AppConstants.vehicleMultipliers[vehicleType] ?? 1.0;
    final distanceCost = distanceKm * AppConstants.perKmRate;
    final timeCost = durationMinutes * AppConstants.perMinuteRate;
    final total = (AppConstants.baseFare + distanceCost + timeCost + AppConstants.bookingFee) * multiplier;
    return total < AppConstants.minimumFare ? AppConstants.minimumFare : double.parse(total.toStringAsFixed(2));
  }

  List<Map<String, dynamic>> getNearbyDrivers(double lat, double lng) {
    final random = Random();
    return List.generate(5, (index) {
      final dLat = (random.nextDouble() - 0.5) * 0.02;
      final dLng = (random.nextDouble() - 0.5) * 0.02;
      return {
        'id': 'driver_${index + 1}',
        'name': ['James Wilson', 'Maria Garcia', 'Ahmed Khan', 'Lisa Chen', 'David Brown'][index],
        'lat': lat + dLat,
        'lng': lng + dLng,
        'rating': 4.5 + random.nextDouble() * 0.5,
        'vehicleType': ['economy', 'comfort', 'premium', 'economy', 'xl'][index],
        'vehicleModel': ['Toyota Camry', 'Honda Accord', 'BMW 5 Series', 'Hyundai Sonata', 'Chevrolet Suburban'][index],
        'vehiclePlate': 'ABC ${1000 + random.nextInt(9000)}',
        'eta': 3 + random.nextInt(12),
      };
    });
  }

  double _calculateDistance(double lat1, double lng1, double lat2, double lng2) {
    const earthRadius = 6371.0;
    final dLat = _toRadians(lat2 - lat1);
    final dLng = _toRadians(lng2 - lng1);
    final a = sin(dLat / 2) * sin(dLat / 2) +
        cos(_toRadians(lat1)) * cos(_toRadians(lat2)) * sin(dLng / 2) * sin(dLng / 2);
    final c = 2 * atan2(sqrt(a), sqrt(1 - a));
    return double.parse((earthRadius * c).toStringAsFixed(2));
  }

  double _toRadians(double degrees) => degrees * pi / 180;

  int _estimateDuration(double distanceKm) {
    return (distanceKm * 2.5).round();
  }
}
