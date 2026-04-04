import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/models/tracking_enums.dart';
import '../../../core/providers/providers.dart';
import '../../../core/widgets/tracking_card.dart';
import '../../../core/widgets/empty_state.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final items = ref.watch(filteredTrackingProvider);
    final itemsAsync = ref.watch(trackingItemsProvider);
    final searchQuery = ref.watch(searchQueryProvider);
    final typeFilter = ref.watch(selectedTypeFilterProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('eTrack'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => context.push('/settings'),
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Search tracking numbers or labels...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () =>
                            ref.read(searchQueryProvider.notifier).state = '',
                      )
                    : null,
                isDense: true,
              ),
              onChanged: (v) =>
                  ref.read(searchQueryProvider.notifier).state = v,
            ),
          ),
          SizedBox(
            height: 40,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 12),
              children: [
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: FilterChip(
                    label: const Text('All'),
                    selected: typeFilter == null,
                    onSelected: (_) => ref
                        .read(selectedTypeFilterProvider.notifier)
                        .state = null,
                  ),
                ),
                ...TrackingType.values.map((type) => Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4),
                      child: FilterChip(
                        avatar: Icon(type.icon, size: 16),
                        label: Text(type.label),
                        selected: typeFilter == type,
                        onSelected: (_) => ref
                            .read(selectedTypeFilterProvider.notifier)
                            .state = typeFilter == type ? null : type,
                      ),
                    )),
              ],
            ),
          ),
          const SizedBox(height: 4),
          Expanded(
            child: itemsAsync.when(
              loading: () =>
                  const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: Text('Error: $e')),
              data: (_) {
                if (items.isEmpty) {
                  return EmptyState(
                    icon: Icons.local_shipping_outlined,
                    title: 'No tracking items',
                    subtitle: searchQuery.isNotEmpty
                        ? 'No results for "$searchQuery"'
                        : 'Tap + to add your first tracking number',
                    actionLabel:
                        searchQuery.isEmpty ? 'Add Tracking' : null,
                    onAction: searchQuery.isEmpty
                        ? () => context.push('/add')
                        : null,
                  );
                }
                return RefreshIndicator(
                  onRefresh: () async {
                    await ref
                        .read(trackingItemsProvider.notifier)
                        .loadItems();
                  },
                  child: ListView.builder(
                    padding: const EdgeInsets.only(bottom: 80),
                    itemCount: items.length,
                    itemBuilder: (context, index) {
                      final item = items[index];
                      return TrackingCard(
                        item: item,
                        onTap: () =>
                            context.push('/detail/${item.id}'),
                      );
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/add'),
        icon: const Icon(Icons.add),
        label: const Text('Track'),
      ),
    );
  }
}
