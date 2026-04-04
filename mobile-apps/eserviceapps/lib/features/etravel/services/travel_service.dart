import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../core/constants/app_constants.dart';
import '../models/booking_model.dart';

class TravelService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Future<String> createBooking({
    required String userId,
    required BookingType type,
    required String origin,
    required String destination,
    required DateTime travelDate,
    required double price,
    String details = '',
  }) async {
    final ref = await _firestore
        .collection(AppConstants.bookingsCollection)
        .add({
          'userId': userId,
          'type': type.name,
          'origin': origin,
          'destination': destination,
          'travelDate': Timestamp.fromDate(travelDate),
          'status': BookingStatus.confirmed.name,
          'price': price,
          'details': details,
          'createdAt': FieldValue.serverTimestamp(),
        });
    return ref.id;
  }

  Stream<List<BookingModel>> getUserBookings(String userId) {
    return _firestore
        .collection(AppConstants.bookingsCollection)
        .where('userId', isEqualTo: userId)
        .orderBy('createdAt', descending: true)
        .limit(50)
        .snapshots()
        .map(
          (snapshot) => snapshot.docs
              .map((doc) => BookingModel.fromMap(doc.data(), doc.id))
              .toList(),
        );
  }

  Future<BookingModel> getBooking(String bookingId) async {
    final doc = await _firestore
        .collection(AppConstants.bookingsCollection)
        .doc(bookingId)
        .get();
    return BookingModel.fromMap(doc.data()!, doc.id);
  }

  Future<void> cancelBooking(String bookingId) async {
    await _firestore
        .collection(AppConstants.bookingsCollection)
        .doc(bookingId)
        .update({'status': BookingStatus.cancelled.name});
  }

  List<Map<String, dynamic>> searchTransport({
    required String origin,
    required String destination,
    required BookingType type,
  }) {
    return List.generate(
      5,
      (i) => <String, dynamic>{
        'name': '${type.name.toUpperCase()} ${i + 1}',
        'departure': DateTime.now()
            .add(Duration(hours: i + 1))
            .toIso8601String(),
        'arrival': DateTime.now().add(Duration(hours: i + 3)).toIso8601String(),
        'price': 15.0 + (i * 5),
        'duration': '${i + 2}h ${(i * 15) % 60}m',
        'type': type.name,
      },
    );
  }
}
