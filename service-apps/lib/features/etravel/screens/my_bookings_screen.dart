import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../../../core/widgets/loading_widget.dart';
import '../providers/travel_provider.dart';

class MyBookingsScreen extends ConsumerWidget {
  const MyBookingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final bookings = ref.watch(userBookingsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('My Bookings')),
      body: bookings.when(
        data: (list) {
          if (list.isEmpty) {
            return const Center(child: Text('No bookings yet'));
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: list.length,
            itemBuilder: (context, index) {
              final b = list[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  onTap: () => context.push('/travel/booking/${b.id}'),
                  leading: CircleAvatar(
                    backgroundColor: AppColors.eTravelColor.withOpacity(0.1),
                    child: Icon(
                      _typeIcon(b.type.name),
                      color: AppColors.eTravelColor,
                    ),
                  ),
                  title: Text('${b.origin} → ${b.destination}'),
                  subtitle: Text(
                    '${b.type.name.toUpperCase()} • ${AppDateUtils.formatDate(b.travelDate)}',
                  ),
                  trailing: Text(
                    AppDateUtils.formatCurrency(b.price),
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              );
            },
          );
        },
        loading: () => const AppLoadingWidget(),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }

  IconData _typeIcon(String type) {
    switch (type) {
      case 'bus':
        return Icons.directions_bus;
      case 'train':
        return Icons.train;
      case 'metro':
        return Icons.subway;
      case 'accommodation':
        return Icons.hotel;
      case 'tour':
        return Icons.tour;
      default:
        return Icons.directions_car;
    }
  }
}
