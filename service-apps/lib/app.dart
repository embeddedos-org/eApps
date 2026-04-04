import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'features/admin/screens/admin_analytics_screen.dart';
import 'features/admin/screens/admin_content_screen.dart';
import 'features/admin/screens/admin_dashboard_screen.dart';
import 'features/admin/screens/admin_users_screen.dart';
import 'features/auth/screens/login_screen.dart';
import 'features/eride/screens/driver_dashboard_screen.dart';
import 'features/eride/screens/ride_booking_screen.dart';
import 'features/esocial/screens/chat_screen.dart';
import 'features/esocial/screens/dating_screen.dart';
import 'features/esocial/screens/groups_screen.dart';
import 'features/esocial/screens/messages_screen.dart';
import 'features/esocial/screens/stories_screen.dart';
import 'features/etrack/screens/tracking_screen.dart';
import 'features/etravel/screens/travel_home_screen.dart';
import 'features/ewallet/screens/ewallet_screen.dart';
import 'features/home/screens/home_screen.dart';
import 'features/notifications/screens/notifications_screen.dart';
import 'features/onboarding/screens/onboarding_screen.dart';
import 'features/settings/screens/settings_screen.dart';
import 'features/wallet/screens/wallet_screen.dart';

final GoRouter _router = GoRouter(
  initialLocation: '/',
  routes: <RouteBase>[
    GoRoute(path: '/', builder: (context, state) => const HomeScreen()),
    GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
    GoRoute(
      path: '/ride',
      builder: (context, state) => const RideBookingScreen(),
    ),
    GoRoute(
      path: '/driver',
      builder: (context, state) => const DriverDashboardScreen(),
    ),
    GoRoute(path: '/chat', builder: (context, state) => const ChatScreen()),
    GoRoute(
      path: '/messages',
      builder: (context, state) => const MessagesScreen(),
    ),
    GoRoute(path: '/groups', builder: (context, state) => const GroupsScreen()),
    GoRoute(
      path: '/stories',
      builder: (context, state) => const StoriesScreen(),
    ),
    GoRoute(path: '/dating', builder: (context, state) => const DatingScreen()),
    GoRoute(
      path: '/tracking',
      builder: (context, state) => const TrackingScreen(),
    ),
    GoRoute(
      path: '/travel',
      builder: (context, state) => const TravelHomeScreen(),
    ),
    GoRoute(
      path: '/ewallet',
      builder: (context, state) => const EWalletScreen(),
    ),
    GoRoute(
      path: '/admin',
      builder: (context, state) => const AdminDashboardScreen(),
    ),
    GoRoute(
      path: '/admin/analytics',
      builder: (context, state) => const AdminAnalyticsScreen(),
    ),
    GoRoute(
      path: '/admin/users',
      builder: (context, state) => const AdminUsersScreen(),
    ),
    GoRoute(
      path: '/admin/content',
      builder: (context, state) => const AdminContentScreen(),
    ),
    GoRoute(
      path: '/settings',
      builder: (context, state) => const SettingsScreen(),
    ),
    GoRoute(
      path: '/notifications',
      builder: (context, state) => const NotificationsScreen(),
    ),
    GoRoute(
      path: '/onboarding',
      builder: (context, state) => const OnboardingScreen(),
    ),
    GoRoute(path: '/wallet', builder: (context, state) => const WalletScreen()),
  ],
);

class EoSuiteApp extends StatelessWidget {
  const EoSuiteApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'EoSuite',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(useMaterial3: true),
      routerConfig: _router,
    );
  }
}
