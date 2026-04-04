import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';

class AdminDashboardScreen extends ConsumerWidget {
  const AdminDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Admin Panel'), backgroundColor: Colors.grey[100]),
      body: SingleChildScrollView(padding: const EdgeInsets.all(16), child: Column(
        crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Overview', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          GridView.count(crossAxisCount: 2, shrinkWrap: true, physics: const NeverScrollableScrollPhysics(),
            mainAxisSpacing: 12, crossAxisSpacing: 12, childAspectRatio: 1.3, children: [
              _StatCard(title: 'Users', value: '1,247', icon: Icons.people, color: AppColors.eSocialColor),
              _StatCard(title: 'Rides', value: '856', icon: Icons.local_taxi, color: AppColors.eRideColor),
              _StatCard(title: 'Bookings', value: '432', icon: Icons.flight, color: AppColors.eTravelColor),
              _StatCard(title: 'Deliveries', value: '2,105', icon: Icons.local_shipping, color: AppColors.eTrackColor),
            ]),
          const SizedBox(height: 24),
          Text('Management', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          _AdminMenuTile(icon: Icons.people_outline, title: 'User Management',
            subtitle: 'View, edit, and manage user accounts', onTap: () => context.push('/admin/users')),
          _AdminMenuTile(icon: Icons.article_outlined, title: 'Content Moderation',
            subtitle: 'Review and moderate posts, comments', onTap: () => context.push('/admin/content')),
          _AdminMenuTile(icon: Icons.analytics_outlined, title: 'Analytics & Reports',
            subtitle: 'Usage stats, revenue, and growth metrics', onTap: () => context.push('/admin/analytics')),
          _AdminMenuTile(icon: Icons.account_balance_wallet_outlined, title: 'Revenue',
            subtitle: 'Micro-fee revenue and transaction logs', onTap: () {}),
          _AdminMenuTile(icon: Icons.settings_outlined, title: 'System Settings',
            subtitle: 'App configuration and feature flags', onTap: () {}),
        ])),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title, value;
  final IconData icon;
  final Color color;
  const _StatCard({required this.title, required this.value, required this.icon, required this.color});

  @override
  Widget build(BuildContext context) {
    return Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(
      crossAxisAlignment: CrossAxisAlignment.start, mainAxisAlignment: MainAxisAlignment.center, children: [
        Icon(icon, color: color, size: 28),
        const Spacer(),
        Text(value, style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: color)),
        Text(title, style: TextStyle(color: Colors.grey[600])),
      ])));
  }
}

class _AdminMenuTile extends StatelessWidget {
  final IconData icon;
  final String title, subtitle;
  final VoidCallback onTap;
  const _AdminMenuTile({required this.icon, required this.title, required this.subtitle, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(margin: const EdgeInsets.only(bottom: 8), child: ListTile(
      leading: Icon(icon, color: AppColors.primary), title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
      subtitle: Text(subtitle), trailing: const Icon(Icons.arrow_forward_ios, size: 16), onTap: onTap));
  }
}
