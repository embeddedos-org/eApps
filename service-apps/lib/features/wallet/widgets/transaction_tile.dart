import 'package:flutter/material.dart';
import '../../../core/models/transaction_model.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';

class TransactionTile extends StatelessWidget {
  final TransactionModel transaction;
  const TransactionTile({super.key, required this.transaction});

  @override
  Widget build(BuildContext context) {
    final isPositive = transaction.amount > 0;
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor:
              isPositive ? AppColors.success.withOpacity(0.1) : AppColors.error.withOpacity(0.1),
          child: Icon(
            isPositive ? Icons.arrow_downward : Icons.arrow_upward,
            color: isPositive ? AppColors.success : AppColors.error,
          ),
        ),
        title: Text(transaction.description),
        subtitle: Text(
          AppDateUtils.timeAgo(transaction.createdAt),
          style: const TextStyle(fontSize: 12),
        ),
        trailing: Text(
          '${isPositive ? '+' : ''}${AppDateUtils.formatCurrency(transaction.amount)}',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: isPositive ? AppColors.success : AppColors.error,
          ),
        ),
      ),
    );
  }
}
