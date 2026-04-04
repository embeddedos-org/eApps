import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/app_constants.dart';
import '../../../core/theme/app_colors.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  final List<Map<String, dynamic>> _pages = [
    {
      'icon': Icons.location_on,
      'title': 'Set Your Destination',
      'description': 'Enter your pickup and drop-off locations. We\'ll find the best route for you.',
      'color': AppColors.primary,
    },
    {
      'icon': Icons.directions_car,
      'title': 'Choose Your Ride',
      'description': 'Select from Economy, Comfort, Premium, or XL vehicles to match your needs and budget.',
      'color': AppColors.info,
    },
    {
      'icon': Icons.navigation,
      'title': 'Track in Real-Time',
      'description': 'Watch your driver approach in real-time. Get live ETA updates and driver details.',
      'color': AppColors.success,
    },
    {
      'icon': Icons.star,
      'title': 'Rate & Ride Again',
      'description': 'Rate your experience, earn rewards, and enjoy seamless rides every time.',
      'color': AppColors.starFilled,
    },
  ];

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Align(
              alignment: Alignment.topRight,
              child: TextButton(
                onPressed: () => context.go(AppConstants.loginRoute),
                child: const Text('Skip'),
              ),
            ),
            Expanded(
              child: PageView.builder(
                controller: _pageController,
                itemCount: _pages.length,
                onPageChanged: (i) => setState(() => _currentPage = i),
                itemBuilder: (context, index) => _buildPage(_pages[index]),
              ),
            ),
            _buildIndicators(),
            const SizedBox(height: 24),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: SizedBox(
                width: double.infinity, height: 52,
                child: ElevatedButton(
                  onPressed: () {
                    if (_currentPage < _pages.length - 1) {
                      _pageController.nextPage(
                        duration: const Duration(milliseconds: 300),
                        curve: Curves.easeInOut,
                      );
                    } else {
                      context.go(AppConstants.loginRoute);
                    }
                  },
                  child: Text(_currentPage < _pages.length - 1
                      ? 'Next' : 'Get Started'),
                ),
              ),
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildPage(Map<String, dynamic> page) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 40),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: (page['color'] as Color).withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(page['icon'] as IconData, size: 80,
                color: page['color'] as Color),
          ),
          const SizedBox(height: 40),
          Text(page['title'] as String,
              style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center),
          const SizedBox(height: 16),
          Text(page['description'] as String,
              style: const TextStyle(fontSize: 16, color: AppColors.textSecondary, height: 1.5),
              textAlign: TextAlign.center),
        ],
      ),
    );
  }

  Widget _buildIndicators() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(_pages.length, (i) => AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        margin: const EdgeInsets.symmetric(horizontal: 4),
        width: _currentPage == i ? 24 : 8,
        height: 8,
        decoration: BoxDecoration(
          color: _currentPage == i ? AppColors.primary : AppColors.divider,
          borderRadius: BorderRadius.circular(4),
        ),
      )),
    );
  }
}
