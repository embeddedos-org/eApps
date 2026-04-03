import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/constants/app_constants.dart';
import '../../../core/utils/validators.dart';
import '../providers/tracking_provider.dart';
import '../models/delivery_model.dart';

class AddTrackingScreen extends ConsumerStatefulWidget {
  const AddTrackingScreen({super.key});

  @override
  ConsumerState<AddTrackingScreen> createState() => _AddTrackingScreenState();
}

class _AddTrackingScreenState extends ConsumerState<AddTrackingScreen> {
  final _formKey = GlobalKey<FormState>();
  final _trackingController = TextEditingController();
  final _descController = TextEditingController();
  String _selectedCarrier = 'USPS';
  DeliveryType _selectedType = DeliveryType.parcel;
  bool _isAdding = false;

  @override
  void dispose() {
    _trackingController.dispose();
    _descController.dispose();
    super.dispose();
  }

  Future<void> _addTracking() async {
    if (!_formKey.currentState!.validate()) return;
    final user = ref.read(currentUserProvider).value;
    if (user == null) return;

    setState(() => _isAdding = true);
    try {
      final id = await ref
          .read(trackingServiceProvider)
          .addTracking(
            userId: user.uid,
            trackingNumber: _trackingController.text.trim(),
            carrier: _selectedCarrier,
            type: _selectedType,
            description: _descController.text.trim(),
          );
      if (mounted) context.go('/track/detail/$id');
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    } finally {
      if (mounted) setState(() => _isAdding = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Add Tracking')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: _trackingController,
                validator: Validators.trackingNumber,
                decoration: const InputDecoration(
                  labelText: 'Tracking Number',
                  prefixIcon: Icon(Icons.qr_code, color: AppColors.eTrackColor),
                  hintText: 'e.g., 1Z999AA10123456784',
                ),
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _selectedCarrier,
                decoration: const InputDecoration(
                  labelText: 'Carrier',
                  prefixIcon: Icon(
                    Icons.local_shipping,
                    color: AppColors.eTrackColor,
                  ),
                ),
                items: AppConstants.supportedCarriers
                    .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                    .toList(),
                onChanged: (v) => setState(() => _selectedCarrier = v!),
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<DeliveryType>(
                value: _selectedType,
                decoration: const InputDecoration(
                  labelText: 'Delivery Type',
                  prefixIcon: Icon(
                    Icons.category,
                    color: AppColors.eTrackColor,
                  ),
                ),
                items: DeliveryType.values
                    .map(
                      (t) => DropdownMenuItem(
                        value: t,
                        child: Text(t.name.toUpperCase()),
                      ),
                    )
                    .toList(),
                onChanged: (v) => setState(() => _selectedType = v!),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _descController,
                decoration: const InputDecoration(
                  labelText: 'Description (optional)',
                  prefixIcon: Icon(
                    Icons.description,
                    color: AppColors.eTrackColor,
                  ),
                  hintText: 'e.g., New laptop from Amazon',
                ),
              ),
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: _isAdding ? null : _addTracking,
                icon: const Icon(Icons.add_circle_outline),
                label: _isAdding
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Text('Track Package'),
                style: FilledButton.styleFrom(
                  backgroundColor: AppColors.eTrackColor,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
