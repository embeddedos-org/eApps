import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

class AdminAnalyticsScreen extends StatelessWidget {
  const AdminAnalyticsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Analytics & Reports')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Platform Metrics',
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _MetricCard(
              title: 'Daily Active Users',
              value: '342',
              change: '+12%',
              positive: true,
            ),
            _MetricCard(
              title: 'Total Revenue',
              value: '\$127.50',
              change: '+8%',
              positive: true,
            ),
            _MetricCard(
              title: 'Avg. Session Time',
              value: '4.2 min',
              change: '-3%',
              positive: false,
            ),
            _MetricCard(
              title: 'Conversion Rate',
              value: '23%',
              change: '+5%',
              positive: true,
            ),
            const SizedBox(height: 24),
            Text(
              'Module Breakdown',
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _ModuleMetric(
              module: 'eSocial',
              users: 856,
              revenue: 42.50,
              color: AppColors.eSocialColor,
            ),
            _ModuleMetric(
              module: 'eRide',
              users: 234,
              revenue: 35.20,
              color: AppColors.eRideColor,
            ),
            _ModuleMetric(
              module: 'eTravel',
              users: 189,
              revenue: 28.80,
              color: AppColors.eTravelColor,
            ),
            _ModuleMetric(
              module: 'eTrack',
              users: 412,
              revenue: 21.00,
              color: AppColors.eTrackColor,
            ),
          ],
        ),
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String title, value, change;
  final bool positive;
  const _MetricCard({
    required this.title,
    required this.value,
    required this.change,
    required this.positive,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: TextStyle(color: Colors.grey[600])),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                color: (positive ? AppColors.success : AppColors.error)
                    .withOpacity(0.1),
              ),
              child: Text(
                change,
                style: TextStyle(
                  color: positive ? AppColors.success : AppColors.error,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ModuleMetric extends StatelessWidget {
  final String module;
  final int users;
  final double revenue;
  final Color color;
  const _ModuleMetric({
    required this.module,
    required this.users,
    required this.revenue,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withOpacity(0.1),
          child: Icon(Icons.bar_chart, color: color),
        ),
        title: Text(
          module,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text('$users active users'),
        trailing: Text(
          '\$${revenue.toStringAsFixed(2)}',
          style: TextStyle(fontWeight: FontWeight.bold, color: color),
        ),
      ),
    );
  }
}
