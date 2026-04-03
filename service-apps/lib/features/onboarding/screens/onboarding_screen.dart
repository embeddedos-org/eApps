import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/constants/app_constants.dart';
import '../../../core/theme/app_colors.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});
  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final _pageController = PageController();
  int _currentPage = 0;

  final _pages = const [
    _OnboardingPage(icon: Icons.apps_rounded, color: AppColors.primary,
      title: 'Welcome to EoSuite', subtitle: 'One app for social, rides, travel, and deliveries'),
    _OnboardingPage(icon: Icons.people_rounded, color: AppColors.eSocialColor,
      title: 'eSocial', subtitle: 'Connect with friends, share stories, find matches'),
    _OnboardingPage(icon: Icons.local_taxi_rounded, color: AppColors.eRideColor,
      title: 'eRide', subtitle: 'Book rides with real-time GPS tracking and ETA'),
    _OnboardingPage(icon: Icons.flight_rounded, color: AppColors.eTravelColor,
      title: 'eTravel', subtitle: 'Book transport, stays, and tours all in one place'),
    _OnboardingPage(icon: Icons.local_shipping_rounded, color: AppColors.eTrackColor,
      title: 'eTrack', subtitle: 'Track all your deliveries from any carrier'),
  ];

  Future<void> _complete() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(AppConstants.onboardingCompleteKey, true);
    if (mounted) context.go('/login');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(child: Column(children: [
        Expanded(child: PageView.builder(
          controller: _pageController, itemCount: _pages.length,
          onPageChanged: (i) => setState(() => _currentPage = i),
          itemBuilder: (ctx, i) => _pages[i])),
        Padding(padding: const EdgeInsets.all(24), child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
            Row(children: List.generate(_pages.length, (i) => Container(
              margin: const EdgeInsets.only(right: 8), width: _currentPage == i ? 24 : 8, height: 8,
              decoration: BoxDecoration(borderRadius: BorderRadius.circular(4),
                color: _currentPage == i ? AppColors.primary : Colors.grey[300])))),
            _currentPage == _pages.length - 1
                ? FilledButton(onPressed: _complete, child: const Text('Get Started'))
                : TextButton(onPressed: _complete, child: const Text('Skip')),
          ])),
      ])),
    );
  }
}

class _OnboardingPage extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;
  final String subtitle;
  const _OnboardingPage({required this.icon, required this.color, required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Padding(padding: const EdgeInsets.all(40), child: Column(
      mainAxisAlignment: MainAxisAlignment.center, children: [
        Container(padding: const EdgeInsets.all(24), decoration: BoxDecoration(
          color: color.withOpacity(0.1), shape: BoxShape.circle),
          child: Icon(icon, size: 80, color: color)),
        const SizedBox(height: 40),
        Text(title, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold), textAlign: TextAlign.center),
        const SizedBox(height: 16),
        Text(subtitle, style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: Colors.grey[600]), textAlign: TextAlign.center),
      ]));
  }
}
