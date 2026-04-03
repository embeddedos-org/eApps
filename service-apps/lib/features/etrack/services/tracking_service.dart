import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../core/constants/app_constants.dart';
import '../models/delivery_model.dart';

class TrackingService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Future<String> addTracking({
    required String userId,
    required String trackingNumber,
    required String carrier,
    required DeliveryType type,
    String description = '',
  }) async {
    final mockEvents = _generateMockEvents(carrier);

    final ref = await _firestore
        .collection(AppConstants.deliveriesCollection)
        .add({
          'userId': userId,
          'trackingNumber': trackingNumber,
          'carrier': carrier,
          'type': type.name,
          'status': DeliveryStatus.inTransit.name,
          'description': description,
          'estimatedDelivery': DateTime.now()
              .add(const Duration(days: 3))
              .toIso8601String(),
          'events': mockEvents.map((e) => e.toMap()).toList(),
          'createdAt': FieldValue.serverTimestamp(),
        });
    return ref.id;
  }

  Stream<List<DeliveryModel>> getActiveDeliveries(String userId) {
    return _firestore
        .collection(AppConstants.deliveriesCollection)
        .where('userId', isEqualTo: userId)
        .where(
          'status',
          whereIn: [
            DeliveryStatus.pending.name,
            DeliveryStatus.pickedUp.name,
            DeliveryStatus.inTransit.name,
            DeliveryStatus.outForDelivery.name,
          ],
        )
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map(
          (snapshot) => snapshot.docs
              .map((doc) => DeliveryModel.fromMap(doc.data(), doc.id))
              .toList(),
        );
  }

  Stream<List<DeliveryModel>> getAllDeliveries(String userId) {
    return _firestore
        .collection(AppConstants.deliveriesCollection)
        .where('userId', isEqualTo: userId)
        .orderBy('createdAt', descending: true)
        .limit(50)
        .snapshots()
        .map(
          (snapshot) => snapshot.docs
              .map((doc) => DeliveryModel.fromMap(doc.data(), doc.id))
              .toList(),
        );
  }

  Future<DeliveryModel> getDelivery(String deliveryId) async {
    final doc = await _firestore
        .collection(AppConstants.deliveriesCollection)
        .doc(deliveryId)
        .get();
    return DeliveryModel.fromMap(doc.data()!, doc.id);
  }

  Stream<DeliveryModel?> watchDelivery(String deliveryId) {
    return _firestore
        .collection(AppConstants.deliveriesCollection)
        .doc(deliveryId)
        .snapshots()
        .map((doc) {
          if (doc.exists) return DeliveryModel.fromMap(doc.data()!, doc.id);
          return null;
        });
  }

  Future<void> deleteTracking(String deliveryId) async {
    await _firestore
        .collection(AppConstants.deliveriesCollection)
        .doc(deliveryId)
        .delete();
  }

  List<TrackingEvent> _generateMockEvents(String carrier) {
    final now = DateTime.now();
    return [
      TrackingEvent(
        status: 'Order Placed',
        location: 'Origin Facility',
        description: 'Package received at $carrier facility',
        timestamp: now.subtract(const Duration(days: 2)),
      ),
      TrackingEvent(
        status: 'In Transit',
        location: 'Sorting Center',
        description: 'Package departed sorting center',
        timestamp: now.subtract(const Duration(days: 1)),
      ),
      TrackingEvent(
        status: 'In Transit',
        location: 'Regional Hub',
        description: 'Arrived at regional distribution hub',
        timestamp: now.subtract(const Duration(hours: 6)),
      ),
    ];
  }
}
