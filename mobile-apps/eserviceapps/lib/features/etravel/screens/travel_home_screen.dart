import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../models/booking_model.dart';

class TravelHomeScreen extends ConsumerStatefulWidget {
  const TravelHomeScreen({super.key});

  @override
  ConsumerState<TravelHomeScreen> createState() => _TravelHomeScreenState();
}

class _TravelHomeScreenState extends ConsumerState<TravelHomeScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('eTravel'),
        backgroundColor: AppColors.eTravelColor.withOpacity(0.05),
        actions: [
          IconButton(
            icon: const Icon(Icons.bookmark_outline),
            onPressed: () => context.push('/travel/bookings'),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          labelColor: AppColors.eTravelColor,
          indicatorColor: AppColors.eTravelColor,
          tabs: const [
            Tab(icon: Icon(Icons.directions_car), text: 'Rides'),
            Tab(icon: Icon(Icons.train), text: 'Transport'),
            Tab(icon: Icon(Icons.hotel), text: 'Stays'),
            Tab(icon: Icon(Icons.tour), text: 'Tours'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _SearchTab(type: BookingType.ride, hint: 'Search rides...'),
          _SearchTab(type: BookingType.train, hint: 'Search buses, trains...'),
          _SearchTab(
            type: BookingType.accommodation,
            hint: 'Search hotels, stays...',
          ),
          _SearchTab(
            type: BookingType.tour,
            hint: 'Search tours, city passes...',
          ),
        ],
      ),
    );
  }
}

class _SearchTab extends StatelessWidget {
  final BookingType type;
  final String hint;

  const _SearchTab({required this.type, required this.hint});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const TextField(
            decoration: InputDecoration(
              labelText: 'From',
              prefixIcon: Icon(
                Icons.my_location,
                color: AppColors.eTravelColor,
              ),
            ),
          ),
          const SizedBox(height: 12),
          const TextField(
            decoration: InputDecoration(
              labelText: 'To',
              prefixIcon: Icon(Icons.location_on, color: AppColors.error),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            readOnly: true,
            decoration: const InputDecoration(
              labelText: 'Date',
              prefixIcon: Icon(
                Icons.calendar_today,
                color: AppColors.eTravelColor,
              ),
            ),
            onTap: () async {
              await showDatePicker(
                context: context,
                initialDate: DateTime.now(),
                firstDate: DateTime.now(),
                lastDate: DateTime.now().add(const Duration(days: 365)),
              );
            },
          ),
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: () => context.push('/travel/search'),
            icon: const Icon(Icons.search),
            label: const Text('Search'),
            style: FilledButton.styleFrom(
              backgroundColor: AppColors.eTravelColor,
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
          ),
          const SizedBox(height: 32),
          Text(
            'Popular Destinations',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 12),
          _DestinationCard(
            name: 'San Francisco',
            subtitle: 'From \$25',
            icon: Icons.location_city,
          ),
          _DestinationCard(
            name: 'Los Angeles',
            subtitle: 'From \$35',
            icon: Icons.beach_access,
          ),
          _DestinationCard(
            name: 'New York',
            subtitle: 'From \$45',
            icon: Icons.apartment,
          ),
        ],
      ),
    );
  }
}

class _DestinationCard extends StatelessWidget {
  final String name;
  final String subtitle;
  final IconData icon;

  const _DestinationCard({
    required this.name,
    required this.subtitle,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: AppColors.eTravelColor.withOpacity(0.1),
          child: Icon(icon, color: AppColors.eTravelColor),
        ),
        title: Text(name),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
      ),
    );
  }
}
