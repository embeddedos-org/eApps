import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'core/providers/auth_provider.dart';
import 'features/auth/screens/login_screen.dart';
import 'features/auth/screens/register_screen.dart';
import 'features/onboarding/screens/onboarding_screen.dart';
import 'features/settings/screens/settings_screen.dart';
import 'features/tracking/screens/track_home_screen.dart';
import 'features/tracking/screens/add_tracking_screen.dart';
import 'features/tracking/screens/tracking_detail_screen.dart';
import 'features/tracking/screens/delivery_history_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: '/',
    redirect: (context, state) {
      final isLoggedIn = authState.value != null;
      final isAuthRoute = state.matchedLocation == '/login' ||
          state.matchedLocation == '/register' ||
          state.matchedLocation == '/onboarding';

      if (!isLoggedIn && !isAuthRoute) {
        return '/login';
      }
      if (isLoggedIn && isAuthRoute) {
        return '/';
      }
      return null;
    },
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const TrackHomeScreen(),
      ),
      GoRoute(
        path: '/onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register',
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/add-tracking',
        builder: (context, state) => const AddTrackingScreen(),
      ),
      GoRoute(
        path: '/tracking/:id',
        builder: (context, state) => TrackingDetailScreen(
          deliveryId: state.pathParameters['id']!,
        ),
      ),
      GoRoute(
        path: '/history',
        builder: (context, state) => const DeliveryHistoryScreen(),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreen(),
      ),
    ],
  );
});
