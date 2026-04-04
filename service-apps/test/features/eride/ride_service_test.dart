import 'package:flutter_test/flutter_test.dart';

import 'package:eosuite/features/eride/services/ride_service.dart';
import '../../helpers/mock_firebase.dart';

void main() {
  setupFirebaseCoreMocks();

  group('RideService', () {
    late RideService rideService;

    setUp(() {
      rideService = RideService();
    });

    test('bookRide returns a ride map', () async {
      final result = await rideService.bookRide(
        pickup: 'Location A',
        destination: 'Location B',
      );
      expect(result, isNotNull);
      expect(result!['status'], 'booked');
    });

    test('cancelRide completes without error', () async {
      await rideService.cancelRide('ride_001');
    });
  });
}
