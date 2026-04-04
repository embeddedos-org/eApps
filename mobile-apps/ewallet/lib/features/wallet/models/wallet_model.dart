import 'package:cloud_firestore/cloud_firestore.dart';
import 'transaction_model.dart';

class WalletModel {
  final double balance;
  final String currency;
  final List<TransactionModel> recentTransactions;
  final DateTime? updatedAt;

  const WalletModel({
    this.balance = 0.0,
    this.currency = 'USD',
    this.recentTransactions = const [],
    this.updatedAt,
  });

  factory WalletModel.fromFirestore(
    DocumentSnapshot doc, {
    List<TransactionModel>? transactions,
  }) {
    final data = doc.data() as Map<String, dynamic>;
    return WalletModel(
      balance: (data['balance'] ?? 0).toDouble(),
      currency: data['currency'] ?? 'USD',
      recentTransactions: transactions ?? [],
      updatedAt: (data['updatedAt'] as Timestamp?)?.toDate(),
    );
  }

  WalletModel copyWith({
    double? balance,
    String? currency,
    List<TransactionModel>? recentTransactions,
    DateTime? updatedAt,
  }) {
    return WalletModel(
      balance: balance ?? this.balance,
      currency: currency ?? this.currency,
      recentTransactions: recentTransactions ?? this.recentTransactions,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  String get formattedBalance => '\$${balance.toStringAsFixed(2)}';

  double get totalIncome => recentTransactions
      .where((t) => t.isCredit)
      .fold(0.0, (sum, t) => sum + t.amount);

  double get totalExpense => recentTransactions
      .where((t) => t.isDebit)
      .fold(0.0, (sum, t) => sum + t.amount);
}
