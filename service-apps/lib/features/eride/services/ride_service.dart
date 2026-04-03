import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../core/constants/app_constants.dart';
import '../models/ride_model.dart';

class RideService {
  late final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Future<String> requestRide({
    required String userId,
    required String vehicleType,
    required double pickupLat,
    required double pickupLng,
    required String pickupAddress,
    required double dropoffLat,
    required double dropoffLng,
    required String dropoffAddress,
    required double fare,
    required double distance,
    required int estimatedMinutes,
  }) async {
    final ref = await _firestore.collection(AppConstants.ridesCollection).add({
      'userId': userId,
      'vehicleType': vehicleType,
      'pickupLat': pickupLat,
      'pickupLng': pickupLng,
      'pickupAddress': pickupAddress,
      'dropoffLat': dropoffLat,
      'dropoffLng': dropoffLng,
      'dropoffAddress': dropoffAddress,
      'status': RideStatus.requested.name,
      'fare': fare,
      'distance': distance,
      'estimatedMinutes': estimatedMinutes,
      'driverId': '',
      'driverName': '',
      'rating': 0,
      'createdAt': FieldValue.serverTimestamp(),
    });
    return ref.id;
  }

  Stream<RideModel?> getRide(String rideId) {
    return _firestore
        .collection(AppConstants.ridesCollection)
        .doc(rideId)
        .snapshots()
        .map((doc) {
          if (doc.exists) return RideModel.fromMap(doc.data()!, doc.id);
          return null;
        });
  }

  Stream<List<RideModel>> getUserRides(String userId) {
    return _firestore
        .collection(AppConstants.ridesCollection)
        .where('userId', isEqualTo: userId)
        .orderBy('createdAt', descending: true)
        .limit(50)
        .snapshots()
        .map(
          (snapshot) => snapshot.docs
              .map((doc) => RideModel.fromMap(doc.data(), doc.id))
              .toList(),
        );
  }

  Stream<RideModel?> getActiveRide(String userId) {
    return _firestore
        .collection(AppConstants.ridesCollection)
        .where('userId', isEqualTo: userId)
        .where(
          'status',
          whereIn: [
            RideStatus.requested.name,
            RideStatus.accepted.name,
            RideStatus.driverEnRoute.name,
            RideStatus.arrived.name,
            RideStatus.inProgress.name,
          ],
        )
        .limit(1)
        .snapshots()
        .map((snapshot) {
          if (snapshot.docs.isEmpty) return null;
          return RideModel.fromMap(
            snapshot.docs.first.data(),
            snapshot.docs.first.id,
          );
        });
  }

  Future<void> cancelRide(String rideId) async {
    await _firestore
        .collection(AppConstants.ridesCollection)
        .doc(rideId)
        .update({'status': RideStatus.cancelled.name});
  }

  Future<void> rateRide(String rideId, double rating) async {
    await _firestore
        .collection(AppConstants.ridesCollection)
        .doc(rideId)
        .update({'rating': rating});
  }

  double calculateFare(String vehicleType, double distanceKm) {
    final rates = {'car': 1.5, 'bike': 0.8, 'taxi': 2.0};
    final rate = rates[vehicleType] ?? 1.5;
    return (rate * distanceKm) + 2.0; // base fare + distance
  }

  int estimateTime(double distanceKm) {
    return (distanceKm * 3).ceil(); // ~3 min per km
  }
}
