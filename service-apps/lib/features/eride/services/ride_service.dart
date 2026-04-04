class RideService {
  Future<Map<String, dynamic>?> bookRide({
    required String pickup,
    required String destination,
  }) async {
    return {
      'id': 'ride_001',
      'pickup': pickup,
      'destination': destination,
      'status': 'booked',
    };
  }

  Future<void> cancelRide(String rideId) async {}
}
