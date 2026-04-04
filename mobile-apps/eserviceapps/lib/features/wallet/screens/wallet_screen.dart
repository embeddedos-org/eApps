import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/wallet_provider.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../../../core/widgets/loading_widget.dart';
import '../widgets/transaction_tile.dart';

class WalletScreen extends ConsumerWidget {
  const WalletScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final balance = ref.watch(walletBalanceProvider);
    final transactions = ref.watch(transactionsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Wallet')),
      body: Column(
        children: [
          Container(
            width: double.infinity,
            margin: const EdgeInsets.all(16),
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [AppColors.primary, AppColors.primaryDark],
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              children: [
                const Text(
                  'Available Balance',
                  style: TextStyle(color: Colors.white70, fontSize: 14),
                ),
                const SizedBox(height: 8),
                balance.when(
                  data: (b) => Text(
                    AppDateUtils.formatCurrency(b),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 36,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  loading: () =>
                      const CircularProgressIndicator(color: Colors.white),
                  error: (_, __) => const Text(
                    '\$0.00',
                    style: TextStyle(color: Colors.white, fontSize: 36),
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    FilledButton.icon(
                      onPressed: () => _showTopUpDialog(context, ref),
                      icon: const Icon(Icons.add),
                      label: const Text('Top Up'),
                      style: FilledButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: AppColors.primary,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                Text(
                  'Recent Transactions',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: transactions.when(
              data: (txns) {
                if (txns.isEmpty) {
                  return const Center(child: Text('No transactions yet'));
                }
                return ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: txns.length,
                  itemBuilder: (context, index) =>
                      TransactionTile(transaction: txns[index]),
                );
              },
              loading: () => const AppLoadingWidget(),
              error: (e, _) => Center(child: Text('Error: $e')),
            ),
          ),
        ],
      ),
    );
  }

  void _showTopUpDialog(BuildContext context, WidgetRef ref) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Top Up Wallet'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(
            labelText: 'Amount (USD)',
            prefixText: '\$ ',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () async {
              final amount = double.tryParse(controller.text);
              if (amount == null || amount <= 0) return;
              final user = ref.read(currentUserProvider).value;
              if (user == null) return;
              await ref.read(walletServiceProvider).topUp(user.uid, amount);
              ref.invalidate(walletBalanceProvider);
              if (ctx.mounted) Navigator.pop(ctx);
            },
            child: const Text('Top Up'),
          ),
        ],
      ),
    );
  }
}
