import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

class DriverDashboardScreen extends StatelessWidget {
  const DriverDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Driver Dashboard'),
        backgroundColor: AppColors.eRideColor.withOpacity(0.05),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Online toggle
            Card(
              child: SwitchListTile(
                title: const Text(
                  'Go Online',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                subtitle: const Text('Accept ride requests'),
                value: true,
                onChanged: (_) {},
                activeColor: AppColors.success,
              ),
            ),
            const SizedBox(height: 16),
            // Stats
            Row(
              children: [
                Expanded(
                  child: _DriverStat(
                    label: 'Today\'s Rides',
                    value: '12',
                    icon: Icons.directions_car,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _DriverStat(
                    label: 'Earnings',
                    value: '\$86.40',
                    icon: Icons.attach_money,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _DriverStat(
                    label: 'Rating',
                    value: '4.8 ★',
                    icon: Icons.star,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _DriverStat(
                    label: 'Acceptance',
                    value: '94%',
                    icon: Icons.check_circle,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            // Map placeholder
            Container(
              height: 200,
              width: double.infinity,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.map, size: 48, color: Colors.grey),
                    SizedBox(height: 8),
                    Text('Live Map', style: TextStyle(color: Colors.grey)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'Incoming Requests',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Card(
              child: ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Color(0xFFE8F5E9),
                  child: Icon(Icons.person, color: AppColors.success),
                ),
                title: const Text('John D. → Market St'),
                subtitle: const Text('2.3 km away • \$12.50'),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.close, color: AppColors.error),
                      onPressed: () {},
                    ),
                    IconButton(
                      icon: const Icon(Icons.check, color: AppColors.success),
                      onPressed: () {},
                    ),
                  ],
                ),
              ),
            ),
            Card(
              child: ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Color(0xFFE8F5E9),
                  child: Icon(Icons.person, color: AppColors.success),
                ),
                title: const Text('Sarah M. → Airport'),
                subtitle: const Text('1.8 km away • \$28.00'),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.close, color: AppColors.error),
                      onPressed: () {},
                    ),
                    IconButton(
                      icon: const Icon(Icons.check, color: AppColors.success),
                      onPressed: () {},
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DriverStat extends StatelessWidget {
  final String label, value;
  final IconData icon;
  const _DriverStat({
    required this.label,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: AppColors.eRideColor),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            Text(
              label,
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }
}
