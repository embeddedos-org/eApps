import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../models/transaction_model.dart';

class TransactionTile extends StatelessWidget {
  final TransactionModel transaction;
  final VoidCallback? onTap;

  const TransactionTile({
    super.key,
    required this.transaction,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            _buildIcon(),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    transaction.description,
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w500,
                      color: AppColors.textPrimary,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 3),
                  Row(
                    children: [
                      _buildStatusBadge(),
                      const SizedBox(width: 8),
                      Text(
                        AppDateUtils.formatTransactionDate(transaction.createdAt),
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppColors.textTertiary,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Text(
              transaction.displayAmount,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: transaction.isCredit
                    ? AppColors.income
                    : AppColors.expense,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIcon() {
    final (icon, color) = _iconAndColor;
    return Container(
      width: 44,
      height: 44,
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Icon(icon, color: color, size: 22),
    );
  }

  (IconData, Color) get _iconAndColor {
    switch (transaction.type) {
      case TransactionType.topUp:
        return (Icons.add_circle_outline_rounded, AppColors.primary);
      case TransactionType.send:
        return (Icons.arrow_upward_rounded, AppColors.expense);
      case TransactionType.receive:
        return (Icons.arrow_downward_rounded, AppColors.income);
      case TransactionType.payment:
        return (Icons.shopping_bag_outlined, AppColors.info);
      case TransactionType.refund:
        return (Icons.replay_rounded, AppColors.warning);
      case TransactionType.withdrawal:
        return (Icons.account_balance_outlined, AppColors.textSecondary);
    }
  }

  Widget _buildStatusBadge() {
    if (transaction.status == TransactionStatus.completed) {
      return const SizedBox.shrink();
    }
    final (label, color) = switch (transaction.status) {
      TransactionStatus.pending => ('Pending', AppColors.warning),
      TransactionStatus.failed => ('Failed', AppColors.error),
      _ => ('', AppColors.textTertiary),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        label,
        style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: color),
      ),
    );
  }
}
