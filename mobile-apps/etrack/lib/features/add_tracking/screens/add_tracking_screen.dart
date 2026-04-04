import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:uuid/uuid.dart';
import '../../../core/models/tracking_enums.dart';
import '../../../core/models/tracking_item.dart';
import '../../../core/providers/providers.dart';
import '../../../core/services/carrier_detector.dart';
import '../../../core/utils/validators.dart';

class AddTrackingScreen extends ConsumerStatefulWidget {
  const AddTrackingScreen({super.key});

  @override
  ConsumerState<AddTrackingScreen> createState() => _AddTrackingScreenState();
}

class _AddTrackingScreenState extends ConsumerState<AddTrackingScreen> {
  final _formKey = GlobalKey<FormState>();
  final _trackingController = TextEditingController();
  final _labelController = TextEditingController();
  bool _isAdding = false;
  CarrierDetectionResult? _detectionResult;
  Carrier? _manualCarrier;
  TrackingType? _manualType;
  final _selectedTags = <TrackingTag>{};

  @override
  void dispose() {
    _trackingController.dispose();
    _labelController.dispose();
    super.dispose();
  }

  void _onTrackingNumberChanged(String value) {
    if (value.trim().length >= 4) {
      final detector = ref.read(carrierDetectorProvider);
      setState(() {
        _detectionResult = detector.detect(value.trim());
        _manualCarrier = null;
        _manualType = null;
      });
    } else {
      setState(() => _detectionResult = null);
    }
  }

  Future<void> _addTracking() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isAdding = true);

    final carrier = _manualCarrier ?? _detectionResult?.carrier ?? Carrier.other;
    final type = _manualType ?? _detectionResult?.trackingType ?? TrackingType.package;
    final now = DateTime.now();

    final statusEngine = ref.read(statusEngineProvider);
    final etaPredictor = ref.read(etaPredictorProvider);
    final eta = etaPredictor.predict(carrier, TrackingStatus.pending, now);

    final item = TrackingItem(
      id: const Uuid().v4(),
      trackingNumber: _trackingController.text.trim(),
      carrier: carrier,
      trackingType: type,
      label: _labelController.text.trim(),
      status: TrackingStatus.pending,
      statusExplanation: 'Tracking added — refresh to get live updates',
      estimatedDelivery: eta.estimatedDate,
      tags: _selectedTags.toList(),
      createdAt: now,
      updatedAt: now,
    );

    await ref.read(trackingItemsProvider.notifier).addItem(item);

    if (mounted) {
      context.pop();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Tracking ${carrier.label} added')),
      );
    }

    setState(() => _isAdding = false);
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
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              TextFormField(
                controller: _trackingController,
                decoration: InputDecoration(
                  labelText: 'Tracking Number',
                  hintText: 'e.g., 1Z999AA10123456784',
                  prefixIcon: const Icon(Icons.qr_code),
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.paste),
                    onPressed: () async {
                      // Clipboard paste would go here
                    },
                  ),
                ),
                validator: Validators.trackingNumber,
                onChanged: _onTrackingNumberChanged,
                textInputAction: TextInputAction.next,
              ),

              if (_detectionResult != null) ...[
                const SizedBox(height: 12),
                Card(
                  color: Theme.of(context).colorScheme.primaryContainer.withOpacity(0.3),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Row(
                      children: [
                        Icon(_detectionResult!.carrier.icon,
                            color: Theme.of(context).colorScheme.primary),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Detected: ${_detectionResult!.carrier.label}',
                                style: const TextStyle(fontWeight: FontWeight.w600),
                              ),
                              Text(
                                '${_detectionResult!.trackingType.label} • '
                                '${(_detectionResult!.confidence * 100).toInt()}% confidence',
                                style: TextStyle(fontSize: 13, color: Colors.grey[600]),
                              ),
                            ],
                          ),
                        ),
                        TextButton(
                          onPressed: () {
                            showModalBottomSheet(
                              context: context,
                              builder: (_) => _CarrierPicker(
                                onSelected: (carrier, type) {
                                  setState(() {
                                    _manualCarrier = carrier;
                                    _manualType = type;
                                  });
                                  Navigator.pop(context);
                                },
                              ),
                            );
                          },
                          child: const Text('Change'),
                        ),
                      ],
                    ),
                  ),
                ),
              ],

              if (_manualCarrier != null) ...[
                const SizedBox(height: 8),
                Chip(
                  avatar: Icon(_manualCarrier!.icon, size: 18),
                  label: Text('${_manualCarrier!.label} (${_manualType?.label ?? "Package"})'),
                  onDeleted: () => setState(() {
                    _manualCarrier = null;
                    _manualType = null;
                  }),
                ),
              ],

              const SizedBox(height: 16),
              TextFormField(
                controller: _labelController,
                decoration: const InputDecoration(
                  labelText: 'Label (optional)',
                  hintText: "e.g., Mom's birthday gift",
                  prefixIcon: Icon(Icons.label_outline),
                ),
                validator: Validators.label,
              ),

              const SizedBox(height: 16),
              const Text('Tags', style: TextStyle(fontWeight: FontWeight.w500)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: TrackingTag.values.map((tag) {
                  final isSelected = _selectedTags.contains(tag);
                  return FilterChip(
                    label: Text(tag.label),
                    selected: isSelected,
                    selectedColor: tag.color.withOpacity(0.2),
                    onSelected: (selected) {
                      setState(() {
                        if (selected) {
                          _selectedTags.add(tag);
                        } else {
                          _selectedTags.remove(tag);
                        }
                      });
                    },
                  );
                }).toList(),
              ),

              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: _isAdding ? null : _addTracking,
                icon: _isAdding
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.add),
                label: Text(_isAdding ? 'Adding...' : 'Add Tracking'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CarrierPicker extends StatelessWidget {
  final void Function(Carrier carrier, TrackingType type) onSelected;

  const _CarrierPicker({required this.onSelected});

  @override
  Widget build(BuildContext context) {
    return ListView(
      shrinkWrap: true,
      children: [
        const Padding(
          padding: EdgeInsets.all(16),
          child: Text('Select Carrier',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        ),
        ...Carrier.values.map((carrier) => ListTile(
              leading: Icon(carrier.icon),
              title: Text(carrier.label),
              subtitle: Text(carrier.fullName),
              onTap: () {
                final type = carrier == Carrier.airline
                    ? TrackingType.flight
                    : carrier == Carrier.uscis
                        ? TrackingType.immigrationCase
                        : TrackingType.package;
                onSelected(carrier, type);
              },
            )),
      ],
    );
  }
}
