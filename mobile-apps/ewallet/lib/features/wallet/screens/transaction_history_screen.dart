import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../../../core/widgets/loading_widget.dart';
import '../../../core/widgets/error_widget.dart';
import '../models/transaction_model.dart';
import '../providers/wallet_provider.dart';
import '../widgets/transaction_tile.dart';

class TransactionHistoryScreen extends ConsumerWidget {
  const TransactionHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final filter = ref.watch(transactionFilterProvider);
    final transactionsAsync = ref.watch(filteredTransactionsProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Transactions'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search_rounded),
            onPressed: () => _showSearch(context, ref),
          ),
        ],
      ),
      body: Column(
        children: [
          SizedBox(
            height: 50,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: [
                _buildFilterChip('All', null, filter, ref),
                _buildFilterChip('Top Up', TransactionType.topUp, filter, ref),
                _buildFilterChip('Sent', TransactionType.send, filter, ref),
                _buildFilterChip('Received', TransactionType.receive, filter, ref),
                _buildFilterChip('Payment', TransactionType.payment, filter, ref),
                _buildFilterChip('Refund', TransactionType.refund, filter, ref),
                _buildFilterChip('Withdrawal', TransactionType.withdrawal, filter, ref),
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: transactionsAsync.when(
              data: (transactions) {
                if (transactions.isEmpty) {
                  return const EmptyStateWidget(
                    message: 'No transactions found',
                    subtitle: 'Try changing the filter',
                    icon: Icons.receipt_long_rounded,
                  );
                }
                final grouped = _groupByDate(transactions);
                return ListView.builder(
                  padding: const EdgeInsets.only(top: 8),
                  itemCount: grouped.length,
                  itemBuilder: (context, index) {
                    final entry = grouped.entries.elementAt(index);
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Padding(
                          padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
                          child: Text(
                            entry.key,
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ),
                        ...entry.value.map((txn) => TransactionTile(
                              transaction: txn,
                              onTap: () => context.push(
                                '/transaction/${txn.id}',
                                extra: txn,
                              ),
                            )),
                      ],
                    );
                  },
                );
              },
              loading: () => const LoadingWidget(),
              error: (e, _) => AppErrorWidget(
                message: 'Failed to load transactions',
                onRetry: () => ref.invalidate(transactionsStreamProvider),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(
    String label,
    TransactionType? type,
    TransactionType? current,
    WidgetRef ref,
  ) {
    final isSelected = current == type;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: FilterChip(
        label: Text(label),
        selected: isSelected,
        onSelected: (_) {
          ref.read(transactionFilterProvider.notifier).state = type;
        },
        selectedColor: AppColors.primary.withOpacity(0.15),
        checkmarkColor: AppColors.primary,
        labelStyle: TextStyle(
          color: isSelected ? AppColors.primary : AppColors.textSecondary,
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
        ),
      ),
    );
  }

  Map<String, List<TransactionModel>> _groupByDate(
      List<TransactionModel> transactions) {
    final Map<String, List<TransactionModel>> grouped = {};
    for (final txn in transactions) {
      final header = AppDateUtils.formatDateGroupHeader(txn.createdAt);
      grouped.putIfAbsent(header, () => []).add(txn);
    }
    return grouped;
  }

  void _showSearch(BuildContext context, WidgetRef ref) {
    showSearch(
      context: context,
      delegate: _TransactionSearchDelegate(ref),
    );
  }
}

class _TransactionSearchDelegate extends SearchDelegate<TransactionModel?> {
  final WidgetRef ref;

  _TransactionSearchDelegate(this.ref);

  @override
  List<Widget> buildActions(BuildContext context) {
    return [
      IconButton(
        icon: const Icon(Icons.clear_rounded),
        onPressed: () => query = '',
      ),
    ];
  }

  @override
  Widget buildLeading(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.arrow_back_rounded),
      onPressed: () => close(context, null),
    );
  }

  @override
  Widget buildResults(BuildContext context) => _buildSearchResults();

  @override
  Widget buildSuggestions(BuildContext context) => _buildSearchResults();

  Widget _buildSearchResults() {
    final transactionsAsync = ref.watch(transactionsStreamProvider);
    return transactionsAsync.when(
      data: (transactions) {
        final filtered = transactions.where((t) {
          final q = query.toLowerCase();
          return t.description.toLowerCase().contains(q) ||
              (t.recipientName?.toLowerCase().contains(q) ?? false) ||
              t.typeLabel.toLowerCase().contains(q);
        }).toList();
        if (filtered.isEmpty) {
          return const Center(
            child: Text('No transactions found',
                style: TextStyle(color: AppColors.textSecondary)),
          );
        }
        return ListView.builder(
          itemCount: filtered.length,
          itemBuilder: (context, index) {
            final txn = filtered[index];
            return TransactionTile(
              transaction: txn,
              onTap: () => close(context, txn),
            );
          },
        );
      },
      loading: () => const LoadingWidget(),
      error: (_, __) => const Center(child: Text('Error loading transactions')),
    );
  }
}
