import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';

class RideHistoryScreen extends ConsumerWidget {
  const RideHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final mockHistory = _getMockHistory();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Ride History'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        actions: [
          IconButton(icon: const Icon(Icons.filter_list), onPressed: () => _showFilterSheet(context)),
        ],
      ),
      body: Column(
        children: [
          _buildSummaryCards(),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: mockHistory.length,
              itemBuilder: (context, index) => _buildRideCard(context, mockHistory[index]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryCards() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(child: _buildStatCard('Total Rides', '47', Icons.directions_car, AppColors.primary)),
          const SizedBox(width: 12),
          Expanded(child: _buildStatCard('Total Spent', '\$842', Icons.attach_money, AppColors.success)),
          const SizedBox(width: 12),
          Expanded(child: _buildStatCard('Avg Rating', '4.9', Icons.star, AppColors.starFilled)),
        ],
      ),
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 8),
            Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: color)),
            const SizedBox(height: 2),
            Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
          ],
        ),
      ),
    );
  }

  Widget _buildRideCard(BuildContext context, Map<String, dynamic> ride) {
    final isCancelled = ride['status'] == 'Cancelled';
    final statusColor = isCancelled ? AppColors.error : AppColors.success;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () => _showRideDetails(context, ride),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(ride['date'] as String,
                      style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(ride['status'] as String,
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: statusColor)),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Column(children: [
                    const Icon(Icons.circle, color: AppColors.mapPickup, size: 10),
                    Container(width: 2, height: 20, color: AppColors.divider),
                    const Icon(Icons.location_on, color: AppColors.mapDropoff, size: 14),
                  ]),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(ride['from'] as String,
                            style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 13)),
                        const SizedBox(height: 10),
                        Text(ride['to'] as String,
                            style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 13)),
                      ],
                    ),
                  ),
                ],
              ),
              const Divider(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(children: [
                    const CircleAvatar(
                      radius: 14, backgroundColor: AppColors.surfaceVariant,
                      child: Icon(Icons.person, size: 16, color: AppColors.textSecondary),
                    ),
                    const SizedBox(width: 8),
                    Text(ride['driver'] as String, style: const TextStyle(fontSize: 13)),
                  ]),
                  Row(children: [
                    _buildInfoChip(Icons.route, ride['distance'] as String),
                    const SizedBox(width: 8),
                    _buildInfoChip(Icons.access_time, ride['duration'] as String),
                  ]),
                  Text(ride['fare'] as String,
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppColors.primary)),
                ],
              ),
              if (!isCancelled && ride['rating'] != null) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    ...List.generate(5, (i) => Icon(Icons.star, size: 14,
                        color: i < (ride['rating'] as int) ? AppColors.starFilled : AppColors.starEmpty)),
                    const SizedBox(width: 8),
                    Text('${ride['vehicleType']}',
                        style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInfoChip(IconData icon, String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant, borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 10, color: AppColors.textSecondary),
          const SizedBox(width: 3),
          Text(text, style: const TextStyle(fontSize: 10, color: AppColors.textSecondary)),
        ],
      ),
    );
  }

  void _showRideDetails(BuildContext context, Map<String, dynamic> ride) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        expand: false, initialChildSize: 0.6, maxChildSize: 0.85,
        builder: (_, controller) => SingleChildScrollView(
          controller: controller,
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(child: Container(width: 40, height: 4,
                  decoration: BoxDecoration(color: AppColors.divider, borderRadius: BorderRadius.circular(2)))),
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Ride Details', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: ride['status'] == 'Completed'
                          ? AppColors.successLight : AppColors.errorLight,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(ride['status'] as String,
                        style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12,
                            color: ride['status'] == 'Completed' ? AppColors.success : AppColors.error)),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              _buildDetailRow('Date', ride['date'] as String),
              _buildDetailRow('Driver', ride['driver'] as String),
              _buildDetailRow('Vehicle', ride['vehicleType'] as String),
              _buildDetailRow('Distance', ride['distance'] as String),
              _buildDetailRow('Duration', ride['duration'] as String),
              _buildDetailRow('Fare', ride['fare'] as String),
              _buildDetailRow('Payment', 'Wallet'),
              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 12),
              Row(
                children: [
                  Column(children: [
                    const Icon(Icons.circle, color: AppColors.mapPickup, size: 10),
                    Container(width: 2, height: 30, color: AppColors.divider),
                    const Icon(Icons.location_on, color: AppColors.mapDropoff, size: 14),
                  ]),
                  const SizedBox(width: 12),
                  Expanded(child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('PICKUP', style: TextStyle(fontSize: 10, color: AppColors.textSecondary, fontWeight: FontWeight.w600)),
                      Text(ride['from'] as String, style: const TextStyle(fontWeight: FontWeight.w500)),
                      const SizedBox(height: 16),
                      const Text('DROP-OFF', style: TextStyle(fontSize: 10, color: AppColors.textSecondary, fontWeight: FontWeight.w600)),
                      Text(ride['to'] as String, style: const TextStyle(fontWeight: FontWeight.w500)),
                    ],
                  )),
                ],
              ),
              const SizedBox(height: 20),
              Row(children: [
                Expanded(child: OutlinedButton.icon(
                  onPressed: () {}, icon: const Icon(Icons.receipt_long, size: 18),
                  label: const Text('Receipt'),
                )),
                const SizedBox(width: 12),
                Expanded(child: OutlinedButton.icon(
                  onPressed: () {}, icon: const Icon(Icons.help_outline, size: 18),
                  label: const Text('Support'),
                )),
              ]),
              const SizedBox(height: 16),
              SizedBox(width: double.infinity, child: ElevatedButton(
                onPressed: () { Navigator.pop(ctx); },
                child: const Text('Book Again'),
              )),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: AppColors.textSecondary, fontSize: 14)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 14)),
        ],
      ),
    );
  }

  void _showFilterSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Filter Rides', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
              const SizedBox(height: 16),
              Wrap(spacing: 8, runSpacing: 8, children: [
                FilterChip(label: const Text('All'), selected: true, onSelected: (_) {}),
                FilterChip(label: const Text('Completed'), selected: false, onSelected: (_) {}),
                FilterChip(label: const Text('Cancelled'), selected: false, onSelected: (_) {}),
                FilterChip(label: const Text('This Week'), selected: false, onSelected: (_) {}),
                FilterChip(label: const Text('This Month'), selected: false, onSelected: (_) {}),
              ]),
              const SizedBox(height: 20),
              SizedBox(width: double.infinity, child: ElevatedButton(
                onPressed: () => Navigator.pop(ctx), child: const Text('Apply'),
              )),
            ],
          ),
        ),
      ),
    );
  }

  List<Map<String, dynamic>> _getMockHistory() {
    return [
      {'from': '742 Evergreen Terrace', 'to': '1600 Amphitheatre Pkwy', 'date': 'Apr 3, 2026 • 8:30 AM',
       'fare': '\$18.60', 'distance': '12.4 km', 'duration': '22 min', 'driver': 'James W.',
       'status': 'Completed', 'vehicleType': 'Economy', 'rating': 5},
      {'from': 'Office Building A', 'to': 'Downtown Mall', 'date': 'Apr 2, 2026 • 6:15 PM',
       'fare': '\$8.75', 'distance': '5.2 km', 'duration': '14 min', 'driver': 'Maria G.',
       'status': 'Completed', 'vehicleType': 'Comfort', 'rating': 5},
      {'from': 'SFO Airport Terminal 2', 'to': '742 Evergreen Terrace', 'date': 'Mar 30, 2026 • 11:00 PM',
       'fare': '\$45.00', 'distance': '28.3 km', 'duration': '38 min', 'driver': 'Ahmed K.',
       'status': 'Completed', 'vehicleType': 'Premium', 'rating': 4},
      {'from': 'Home', 'to': 'FitLife Gym', 'date': 'Mar 29, 2026 • 7:00 AM',
       'fare': '\$0.00', 'distance': '3.1 km', 'duration': '8 min', 'driver': 'Lisa C.',
       'status': 'Cancelled', 'vehicleType': 'Economy', 'rating': null},
      {'from': 'Blue Bottle Coffee', 'to': 'Office Building A', 'date': 'Mar 28, 2026 • 9:00 AM',
       'fare': '\$9.80', 'distance': '6.7 km', 'duration': '16 min', 'driver': 'David B.',
       'status': 'Completed', 'vehicleType': 'Economy', 'rating': 5},
      {'from': 'Union Square', 'to': 'Golden Gate Park', 'date': 'Mar 25, 2026 • 2:30 PM',
       'fare': '\$14.20', 'distance': '8.9 km', 'duration': '20 min', 'driver': 'Sarah T.',
       'status': 'Completed', 'vehicleType': 'Comfort', 'rating': 4},
    ];
  }
}
