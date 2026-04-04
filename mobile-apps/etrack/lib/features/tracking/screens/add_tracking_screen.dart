import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/constants/app_constants.dart';
import '../../../core/utils/validators.dart';
import '../../../core/providers/auth_provider.dart';
import '../providers/tracking_provider.dart';

class AddTrackingScreen extends ConsumerStatefulWidget {
  const AddTrackingScreen({super.key});

  @override
  ConsumerState<AddTrackingScreen> createState() => _AddTrackingScreenState();
}

class _AddTrackingScreenState extends ConsumerState<AddTrackingScreen> {
  final _formKey = GlobalKey<FormState>();
  final _trackingController = TextEditingController();
  final _packageNameController = TextEditingController();
  String _selectedCarrier = AppConstants.supportedCarriers.first;
  bool _isLoading = false;

  @override
  void dispose() {
    _trackingController.dispose();
    _packageNameController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    final user = ref.read(authStateProvider).value;
    if (user == null) return;

    setState(() => _isLoading = true);

    try {
      final trackingService = ref.read(trackingServiceProvider);
      await trackingService.addTracking(
        userId: user.uid,
        trackingNumber: _trackingController.text.trim(),
        carrier: _selectedCarrier,
        packageName: _packageNameController.text.trim().isEmpty
            ? null
            : _packageNameController.text.trim(),
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Package added successfully!'),
            backgroundColor: AppColors.success,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
        );
        context.pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to add package: $e'),
            backgroundColor: AppColors.error,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Add Package'),
        leading: IconButton(
          icon: const Icon(Icons.close_rounded),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      AppColors.primary.withOpacity(0.08),
                      AppColors.primary.withOpacity(0.02),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppColors.primary.withOpacity(0.15)),
                ),
                child: const Column(
                  children: [
                    Icon(Icons.local_shipping_rounded,
                        size: 40, color: AppColors.primary),
                    SizedBox(height: 12),
                    Text(
                      'Track a Package',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w700,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'Enter your tracking details below',
                      style: TextStyle(
                        fontSize: 14,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 28),
              const Text(
                'TRACKING NUMBER',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textSecondary,
                  letterSpacing: 1.0,
                ),
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _trackingController,
                validator: Validators.trackingNumber,
                textCapitalization: TextCapitalization.characters,
                decoration: InputDecoration(
                  hintText: 'e.g. 1Z999AA10123456784',
                  prefixIcon:
                      const Icon(Icons.qr_code_rounded, color: AppColors.primary),
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.qr_code_scanner_rounded),
                    tooltip: 'Scan Barcode',
                    color: AppColors.primary,
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: const Text('Barcode scanner coming soon!'),
                          behavior: SnackBarBehavior.floating,
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10)),
                        ),
                      );
                    },
                  ),
                ),
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 24),
              const Text(
                'CARRIER',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textSecondary,
                  letterSpacing: 1.0,
                ),
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: _selectedCarrier,
                onChanged: (value) {
                  if (value != null) setState(() => _selectedCarrier = value);
                },
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.business_rounded, color: AppColors.primary),
                ),
                items: AppConstants.supportedCarriers.map((carrier) {
                  return DropdownMenuItem(
                    value: carrier,
                    child: Row(
                      children: [
                        Icon(
                          _carrierIcon(carrier),
                          size: 20,
                          color: AppColors.primary,
                        ),
                        const SizedBox(width: 12),
                        Text(carrier),
                      ],
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 24),
              const Text(
                'PACKAGE NAME (OPTIONAL)',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textSecondary,
                  letterSpacing: 1.0,
                ),
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _packageNameController,
                decoration: const InputDecoration(
                  hintText: 'e.g. New Headphones, Birthday Gift...',
                  prefixIcon:
                      Icon(Icons.label_outline_rounded, color: AppColors.primary),
                ),
              ),
              const SizedBox(height: 36),
              SizedBox(
                height: 52,
                child: ElevatedButton.icon(
                  onPressed: _isLoading ? null : _submit,
                  icon: _isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.add_rounded),
                  label: Text(_isLoading ? 'Adding...' : 'Start Tracking'),
                ),
              ),
              const SizedBox(height: 20),
              OutlinedButton.icon(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: const Text('Barcode scanner coming soon!'),
                      behavior: SnackBarBehavior.floating,
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10)),
                    ),
                  );
                },
                icon: const Icon(Icons.qr_code_scanner_rounded),
                label: const Text('Scan Barcode Instead'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData _carrierIcon(String carrier) {
    switch (carrier) {
      case 'USPS':
        return Icons.local_post_office_rounded;
      case 'FedEx':
        return Icons.flight_rounded;
      case 'UPS':
        return Icons.inventory_2_rounded;
      case 'DHL':
        return Icons.rocket_launch_rounded;
      case 'India Post':
        return Icons.markunread_mailbox_rounded;
      case 'Australia Post':
        return Icons.mail_rounded;
      case 'NZ Post':
        return Icons.mail_outline_rounded;
      case 'Singapore Post':
        return Icons.mark_email_read_rounded;
      default:
        return Icons.local_shipping_rounded;
    }
  }
}
