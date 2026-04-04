import 'dart:math';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:uuid/uuid.dart';
import '../../../core/constants/app_constants.dart';
import '../models/delivery_model.dart';

class TrackingService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final _uuid = const Uuid();

  Stream<List<DeliveryModel>> getActiveDeliveries(String userId) {
    return _firestore
        .collection(AppConstants.deliveriesCollection)
        .where('userId', isEqualTo: userId)
        .where('status', whereNotIn: ['delivered'])
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map((snapshot) => snapshot.docs
            .map((doc) => DeliveryModel.fromFirestore(doc))
            .toList());
  }

  Stream<List<DeliveryModel>> getDeliveryHistory(String userId) {
    return _firestore
        .collection(AppConstants.deliveriesCollection)
        .where('userId', isEqualTo: userId)
        .where('status', isEqualTo: 'delivered')
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map((snapshot) => snapshot.docs
            .map((doc) => DeliveryModel.fromFirestore(doc))
            .toList());
  }

  Stream<DeliveryModel?> getDelivery(String deliveryId) {
    return _firestore
        .collection(AppConstants.deliveriesCollection)
        .doc(deliveryId)
        .snapshots()
        .map((doc) => doc.exists ? DeliveryModel.fromFirestore(doc) : null);
  }

  Future<DeliveryModel> addTracking({
    required String userId,
    required String trackingNumber,
    required String carrier,
    String? packageName,
  }) async {
    final mockInfo = mockFetchTrackingInfo(trackingNumber, carrier);

    final delivery = DeliveryModel(
      id: _uuid.v4(),
      userId: userId,
      trackingNumber: trackingNumber,
      carrier: carrier,
      packageName: packageName ?? 'Package',
      status: mockInfo['status'] as DeliveryStatus,
      estimatedDelivery: mockInfo['estimatedDelivery'] as DateTime?,
      events: mockInfo['events'] as List<TrackingEvent>,
      createdAt: DateTime.now(),
    );

    final docRef = await _firestore
        .collection(AppConstants.deliveriesCollection)
        .add(delivery.toFirestore());

    return DeliveryModel(
      id: docRef.id,
      userId: delivery.userId,
      trackingNumber: delivery.trackingNumber,
      carrier: delivery.carrier,
      packageName: delivery.packageName,
      status: delivery.status,
      estimatedDelivery: delivery.estimatedDelivery,
      events: delivery.events,
      createdAt: delivery.createdAt,
    );
  }

  Future<void> removeTracking(String deliveryId) async {
    await _firestore
        .collection(AppConstants.deliveriesCollection)
        .doc(deliveryId)
        .delete();
  }

  Future<void> updateStatus(
    String deliveryId,
    DeliveryStatus newStatus,
    TrackingEvent event,
  ) async {
    final doc = await _firestore
        .collection(AppConstants.deliveriesCollection)
        .doc(deliveryId)
        .get();

    if (!doc.exists) return;

    final delivery = DeliveryModel.fromFirestore(doc);
    final updatedEvents = [event, ...delivery.events];

    await _firestore
        .collection(AppConstants.deliveriesCollection)
        .doc(deliveryId)
        .update({
      'status': newStatus.name,
      'events': updatedEvents.map((e) => e.toMap()).toList(),
    });
  }

  Future<void> refreshTracking(String deliveryId) async {
    final doc = await _firestore
        .collection(AppConstants.deliveriesCollection)
        .doc(deliveryId)
        .get();

    if (!doc.exists) return;

    final delivery = DeliveryModel.fromFirestore(doc);
    final mockInfo = mockFetchTrackingInfo(delivery.trackingNumber, delivery.carrier);
    final newEvents = mockInfo['events'] as List<TrackingEvent>;
    final newStatus = mockInfo['status'] as DeliveryStatus;

    await _firestore
        .collection(AppConstants.deliveriesCollection)
        .doc(deliveryId)
        .update({
      'status': newStatus.name,
      'events': newEvents.map((e) => e.toMap()).toList(),
      'estimatedDelivery': mockInfo['estimatedDelivery'] != null
          ? Timestamp.fromDate(mockInfo['estimatedDelivery'] as DateTime)
          : null,
    });
  }

  Map<String, dynamic> mockFetchTrackingInfo(String trackingNumber, String carrier) {
    final random = Random(trackingNumber.hashCode);
    final statusIndex = random.nextInt(5);
    final status = DeliveryStatus.values[statusIndex];

    final now = DateTime.now();
    final cities = [
      'New York, NY',
      'Los Angeles, CA',
      'Chicago, IL',
      'Houston, TX',
      'Phoenix, AZ',
      'San Francisco, CA',
      'Seattle, WA',
      'Denver, CO',
      'Atlanta, GA',
      'Miami, FL',
      'Mumbai, India',
      'Sydney, Australia',
      'Auckland, NZ',
      'Singapore',
    ];

    final descriptions = {
      DeliveryStatus.ordered: [
        'Order placed successfully',
        'Label created, awaiting pickup',
        'Shipment information received',
      ],
      DeliveryStatus.shipped: [
        'Package picked up by $carrier',
        'Departed from origin facility',
        'In transit to sorting center',
      ],
      DeliveryStatus.inTransit: [
        'Arrived at regional distribution center',
        'Departed sorting facility',
        'In transit to destination city',
        'Cleared customs',
        'Transferred between facilities',
      ],
      DeliveryStatus.outForDelivery: [
        'Out for delivery',
        'With delivery courier',
        'Arriving today by end of day',
      ],
      DeliveryStatus.delivered: [
        'Delivered — left at front door',
        'Delivered — signed by recipient',
        'Delivered — handed to resident',
      ],
    };

    final events = <TrackingEvent>[];
    for (int i = statusIndex; i >= 0; i--) {
      final s = DeliveryStatus.values[i];
      final descs = descriptions[s] ?? ['Status update'];
      final desc = descs[random.nextInt(descs.length)];
      final city = cities[random.nextInt(cities.length)];
      final hoursAgo = (statusIndex - i) * 18 + random.nextInt(12);

      events.add(TrackingEvent(
        status: s.label,
        location: city,
        timestamp: now.subtract(Duration(hours: hoursAgo)),
        description: desc,
      ));
    }

    events.sort((a, b) => b.timestamp.compareTo(a.timestamp));

    final estimatedDelivery = status == DeliveryStatus.delivered
        ? events.first.timestamp
        : now.add(Duration(days: random.nextInt(5) + 1));

    return {
      'status': status,
      'estimatedDelivery': estimatedDelivery,
      'events': events,
    };
  }
}
