import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/utils/validators.dart';
import '../providers/wallet_provider.dart';

class SendMoneyScreen extends ConsumerStatefulWidget {
  const SendMoneyScreen({super.key});

  @override
  ConsumerState<SendMoneyScreen> createState() => _SendMoneyScreenState();
}

class _SendMoneyScreenState extends ConsumerState<SendMoneyScreen> {
  final _formKey = GlobalKey<FormState>();
  final _recipientController = TextEditingController();
  final _amountController = TextEditingController();
  final _noteController = TextEditingController();
  String? _selectedRecipientId;
  String? _selectedRecipientName;

  final _recentRecipients = [
    _Recipient('r1', 'Alice Johnson', 'alice@email.com'),
    _Recipient('r2', 'Bob Smith', 'bob@email.com'),
    _Recipient('r3', 'Carol Williams', 'carol@email.com'),
    _Recipient('r4', 'David Brown', 'david@email.com'),
  ];

  @override
  void dispose() {
    _recipientController.dispose();
    _amountController.dispose();
    _noteController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final sendState = ref.watch(sendMoneyProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('Send Money')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Recent Recipients',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                height: 90,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: _recentRecipients.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 16),
                  itemBuilder: (context, index) {
                    final r = _recentRecipients[index];
                    final isSelected = _selectedRecipientId == r.id;
                    return GestureDetector(
                      onTap: () {
                        setState(() {
                          _selectedRecipientId = r.id;
                          _selectedRecipientName = r.name;
                          _recipientController.text = r.name;
                        });
                      },
                      child: Column(
                        children: [
                          Container(
                            width: 56,
                            height: 56,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: isSelected
                                  ? AppColors.primary
                                  : AppColors.primary.withOpacity(0.1),
                              border: isSelected
                                  ? Border.all(color: AppColors.accent, width: 2)
                                  : null,
                            ),
                            child: Center(
                              child: Text(
                                r.name[0].toUpperCase(),
                                style: TextStyle(
                                  fontSize: 22,
                                  fontWeight: FontWeight.w600,
                                  color: isSelected ? Colors.white : AppColors.primary,
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            r.name.split(' ').first,
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                              color: isSelected
                                  ? AppColors.primary
                                  : AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 24),
              TextFormField(
                controller: _recipientController,
                decoration: InputDecoration(
                  labelText: 'Recipient',
                  hintText: 'Enter name or email',
                  prefixIcon: const Icon(Icons.person_search_rounded),
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.qr_code_scanner_rounded),
                    onPressed: () {},
                  ),
                ),
                validator: (v) => Validators.required(v, 'Recipient'),
                onChanged: (val) {
                  final match = _recentRecipients.where(
                    (r) => r.name.toLowerCase().contains(val.toLowerCase()),
                  );
                  if (match.isNotEmpty) {
                    setState(() {
                      _selectedRecipientId = match.first.id;
                      _selectedRecipientName = match.first.name;
                    });
                  }
                },
              ),
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppColors.divider),
                ),
                child: Column(
                  children: [
                    const Text(
                      'Amount',
                      style: TextStyle(
                        fontSize: 14,
                        color: AppColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _amountController,
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      inputFormatters: [
                        FilteringTextInputFormatter.allow(RegExp(r'^\d+\.?\d{0,2}')),
                      ],
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 40,
                        fontWeight: FontWeight.w700,
                        color: AppColors.textPrimary,
                      ),
                      decoration: const InputDecoration(
                        border: InputBorder.none,
                        enabledBorder: InputBorder.none,
                        focusedBorder: InputBorder.none,
                        hintText: '\$0.00',
                        hintStyle: TextStyle(
                          fontSize: 40,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textTertiary,
                        ),
                        fillColor: Colors.transparent,
                        filled: true,
                        prefixText: '\$ ',
                        prefixStyle: TextStyle(
                          fontSize: 40,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      validator: Validators.amount,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              TextFormField(
                controller: _noteController,
                decoration: const InputDecoration(
                  labelText: 'Note (optional)',
                  hintText: 'What\'s this for?',
                  prefixIcon: Icon(Icons.note_alt_outlined),
                ),
                maxLines: 2,
                maxLength: 100,
              ),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: !sendState.isLoading ? _handleSend : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    disabledBackgroundColor: AppColors.primary.withOpacity(0.3),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                  child: sendState.isLoading
                      ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2.5,
                          ),
                        )
                      : const Text(
                          'Continue',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Colors.white,
                          ),
                        ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _handleSend() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedRecipientId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a recipient')),
      );
      return;
    }

    final confirmed = await _showPinDialog();
    if (!confirmed) return;

    final user = ref.read(authNotifierProvider).user;
    if (user == null) return;

    final amount = double.parse(_amountController.text);
    final success = await ref.read(sendMoneyProvider.notifier).send(
          senderId: user.id,
          recipientId: _selectedRecipientId!,
          recipientName: _selectedRecipientName!,
          amount: amount,
          note: _noteController.text.isNotEmpty ? _noteController.text : null,
        );

    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Sent \$${amount.toStringAsFixed(2)} to $_selectedRecipientName'),
          backgroundColor: AppColors.success,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
      context.pop();
    }
  }

  Future<bool> _showPinDialog() async {
    final pinController = TextEditingController();
    bool? result = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) {
        String? error;
        return StatefulBuilder(
          builder: (ctx, setDialogState) {
            return AlertDialog(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              title: const Column(
                children: [
                  Icon(Icons.lock_rounded, color: AppColors.primary, size: 40),
                  SizedBox(height: 12),
                  Text(
                    'Enter PIN',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
                  ),
                  SizedBox(height: 4),
                  Text(
                    'Enter your 4-digit PIN to confirm',
                    style: TextStyle(fontSize: 13, color: AppColors.textSecondary, fontWeight: FontWeight.w400),
                  ),
                ],
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextField(
                    controller: pinController,
                    keyboardType: TextInputType.number,
                    obscureText: true,
                    maxLength: 4,
                    textAlign: TextAlign.center,
                    inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                    style: const TextStyle(fontSize: 28, letterSpacing: 16, fontWeight: FontWeight.w700),
                    decoration: InputDecoration(
                      counterText: '',
                      hintText: '••••',
                      hintStyle: const TextStyle(fontSize: 28, letterSpacing: 16, color: AppColors.textTertiary),
                      errorText: error,
                      filled: true,
                      fillColor: AppColors.surfaceVariant,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(ctx, false),
                  child: const Text('Cancel'),
                ),
                ElevatedButton(
                  onPressed: () {
                    if (pinController.text.length == 4) {
                      Navigator.pop(ctx, true);
                    } else {
                      setDialogState(() => error = 'Enter 4-digit PIN');
                    }
                  },
                  child: const Text('Confirm'),
                ),
              ],
            );
          },
        );
      },
    );
    pinController.dispose();
    return result ?? false;
  }
}

class _Recipient {
  final String id;
  final String name;
  final String email;
  _Recipient(this.id, this.name, this.email);
}
