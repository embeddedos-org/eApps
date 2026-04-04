import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/providers/wallet_provider.dart';
import '../../../core/providers/notification_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../widgets/module_card.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(currentUserProvider);
    final balance = ref.watch(walletBalanceProvider);
    final unread = ref.watch(unreadCountProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('EoSuite'),
        actions: [
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined),
                onPressed: () => context.push('/notifications'),
              ),
              unread.when(
                data: (count) => count > 0
                    ? Positioned(
                        right: 6,
                        top: 6,
                        child: Container(
                          padding: const EdgeInsets.all(4),
                          decoration: const BoxDecoration(
                            color: AppColors.error,
                            shape: BoxShape.circle,
                          ),
                          child: Text(
                            '$count',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                            ),
                          ),
                        ),
                      )
                    : const SizedBox.shrink(),
                loading: () => const SizedBox.shrink(),
                error: (_, __) => const SizedBox.shrink(),
              ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.account_balance_wallet_outlined),
            onPressed: () => context.push('/wallet'),
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => ref.read(authServiceProvider).signOut(),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome & Wallet Summary
            user.when(
              data: (u) => Text(
                'Welcome, ${u?.displayName ?? 'User'}!',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              loading: () => const SizedBox.shrink(),
              error: (_, __) => const SizedBox.shrink(),
            ),
            const SizedBox(height: 8),
            // Wallet Card
            GestureDetector(
              onTap: () => context.push('/wallet'),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [AppColors.primary, AppColors.primaryDark],
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Wallet Balance',
                          style: TextStyle(color: Colors.white70, fontSize: 13),
                        ),
                        const SizedBox(height: 4),
                        balance.when(
                          data: (b) => Text(
                            AppDateUtils.formatCurrency(b),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          loading: () => const Text(
                            '...',
                            style: TextStyle(color: Colors.white, fontSize: 28),
                          ),
                          error: (_, __) => const Text(
                            '\$0.00',
                            style: TextStyle(color: Colors.white, fontSize: 28),
                          ),
                        ),
                      ],
                    ),
                    const Icon(Icons.arrow_forward_ios, color: Colors.white70),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'Services',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 12),
            // Module Grid
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 1.1,
              children: [
                ModuleCard(
                  title: 'eSocial',
                  subtitle: 'Social & Dating',
                  icon: Icons.people_rounded,
                  color: AppColors.eSocialColor,
                  onTap: () => context.go('/social'),
                ),
                ModuleCard(
                  title: 'eRide',
                  subtitle: 'Ride Hailing',
                  icon: Icons.local_taxi_rounded,
                  color: AppColors.eRideColor,
                  onTap: () => context.go('/ride'),
                ),
                ModuleCard(
                  title: 'eTravel',
                  subtitle: 'Travel & Booking',
                  icon: Icons.flight_rounded,
                  color: AppColors.eTravelColor,
                  onTap: () => context.go('/travel'),
                ),
                ModuleCard(
                  title: 'eTrack',
                  subtitle: 'Delivery Tracking',
                  icon: Icons.local_shipping_rounded,
                  color: AppColors.eTrackColor,
                  onTap: () => context.go('/track'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
