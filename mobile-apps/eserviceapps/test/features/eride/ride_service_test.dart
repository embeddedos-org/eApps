import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_core_platform_interface/firebase_core_platform_interface.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:eosuite/features/eride/services/ride_service.dart';

void main() {
  setUpAll(() async {
    TestWidgetsFlutterBinding.ensureInitialized();
    setupFirebaseCoreMocks();
  });

  group('RideService', () {
    late RideService service;

    setUp(() async {
      await Firebase.initializeApp();
      service = RideService();
    });

    group('calculateFare', () {
      test('calculates car fare correctly', () {
        final fare = service.calculateFare('car', 10.0);
        expect(fare, 17.0); // 1.5 * 10 + 2.0 base
      });

      test('calculates bike fare correctly', () {
        final fare = service.calculateFare('bike', 10.0);
        expect(fare, 10.0); // 0.8 * 10 + 2.0 base
      });

      test('calculates taxi fare correctly', () {
        final fare = service.calculateFare('taxi', 10.0);
        expect(fare, 22.0); // 2.0 * 10 + 2.0 base
      });

      test('uses default rate for unknown vehicle', () {
        final fare = service.calculateFare('unknown', 10.0);
        expect(fare, 17.0); // defaults to car rate
      });
    });

    group('estimateTime', () {
      test('estimates correctly', () {
        expect(service.estimateTime(10.0), 30); // 3 min per km
        expect(service.estimateTime(1.0), 3);
      });

      test('rounds up fractional times', () {
        expect(service.estimateTime(1.5), 5); // 4.5 rounds up
      });
    });
  });
}
