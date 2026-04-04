import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants/app_constants.dart';
import '../../../core/providers/providers.dart';
import '../../../core/services/api/api_config.dart';
import '../../../core/utils/validators.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  final _uspsController = TextEditingController();
  final _fedexIdController = TextEditingController();
  final _fedexSecretController = TextEditingController();
  final _upsIdController = TextEditingController();
  final _upsSecretController = TextEditingController();
  final _aviationController = TextEditingController();
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadKeys();
  }

  Future<void> _loadKeys() async {
    _uspsController.text = await ApiConfig.getUspsUserId() ?? '';
    _fedexIdController.text = await ApiConfig.getFedexClientId() ?? '';
    _fedexSecretController.text = await ApiConfig.getFedexClientSecret() ?? '';
    _upsIdController.text = await ApiConfig.getUpsClientId() ?? '';
    _upsSecretController.text = await ApiConfig.getUpsClientSecret() ?? '';
    _aviationController.text = await ApiConfig.getAviationStackKey() ?? '';
    setState(() => _loading = false);
  }

  Future<void> _saveKeys() async {
    await ApiConfig.setUspsUserId(_uspsController.text.trim());
    await ApiConfig.setFedexClientId(_fedexIdController.text.trim());
    await ApiConfig.setFedexClientSecret(_fedexSecretController.text.trim());
    await ApiConfig.setUpsClientId(_upsIdController.text.trim());
    await ApiConfig.setUpsClientSecret(_upsSecretController.text.trim());
    await ApiConfig.setAviationStackKey(_aviationController.text.trim());
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('API keys saved')),
      );
    }
  }

  @override
  void dispose() {
    _uspsController.dispose();
    _fedexIdController.dispose();
    _fedexSecretController.dispose();
    _upsIdController.dispose();
    _upsSecretController.dispose();
    _aviationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final themeMode = ref.watch(themeModeProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // Theme
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Appearance',
                            style: TextStyle(
                                fontSize: 16, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 12),
                        SegmentedButton<ThemeMode>(
                          segments: const [
                            ButtonSegment(
                                value: ThemeMode.system,
                                icon: Icon(Icons.settings_brightness),
                                label: Text('System')),
                            ButtonSegment(
                                value: ThemeMode.light,
                                icon: Icon(Icons.light_mode),
                                label: Text('Light')),
                            ButtonSegment(
                                value: ThemeMode.dark,
                                icon: Icon(Icons.dark_mode),
                                label: Text('Dark')),
                          ],
                          selected: {themeMode},
                          onSelectionChanged: (modes) {
                            ref
                                .read(themeModeProvider.notifier)
                                .setThemeMode(modes.first);
                          },
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 16),

                // API Keys
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('API Keys (Optional)',
                            style: TextStyle(
                                fontSize: 16, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 4),
                        Text(
                          'Enter your free API keys to enable live tracking updates. '
                          'Keys are stored locally on your device only.',
                          style: TextStyle(
                              fontSize: 13, color: Colors.grey[600]),
                        ),
                        const SizedBox(height: 16),

                        // USPS
                        const Text('USPS',
                            style: TextStyle(fontWeight: FontWeight.w500)),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: _uspsController,
                          decoration: const InputDecoration(
                            labelText: 'USPS User ID',
                            hintText: 'Register at usps.com/webtools',
                            isDense: true,
                          ),
                          validator: Validators.apiKey,
                        ),

                        const SizedBox(height: 16),

                        // FedEx
                        const Text('FedEx',
                            style: TextStyle(fontWeight: FontWeight.w500)),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: _fedexIdController,
                          decoration: const InputDecoration(
                            labelText: 'Client ID',
                            isDense: true,
                          ),
                        ),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: _fedexSecretController,
                          decoration: const InputDecoration(
                            labelText: 'Client Secret',
                            isDense: true,
                          ),
                          obscureText: true,
                        ),

                        const SizedBox(height: 16),

                        // UPS
                        const Text('UPS',
                            style: TextStyle(fontWeight: FontWeight.w500)),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: _upsIdController,
                          decoration: const InputDecoration(
                            labelText: 'Client ID',
                            isDense: true,
                          ),
                        ),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: _upsSecretController,
                          decoration: const InputDecoration(
                            labelText: 'Client Secret',
                            isDense: true,
                          ),
                          obscureText: true,
                        ),

                        const SizedBox(height: 16),

                        // AviationStack
                        const Text('AviationStack (Flights)',
                            style: TextStyle(fontWeight: FontWeight.w500)),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: _aviationController,
                          decoration: const InputDecoration(
                            labelText: 'API Key',
                            hintText: 'Register at aviationstack.com',
                            isDense: true,
                          ),
                        ),

                        const SizedBox(height: 16),
                        FilledButton.icon(
                          onPressed: _saveKeys,
                          icon: const Icon(Icons.save),
                          label: const Text('Save API Keys'),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 16),

                // Data Management
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Data',
                            style: TextStyle(
                                fontSize: 16, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 8),
                        ListTile(
                          leading: const Icon(Icons.delete_forever,
                              color: Colors.red),
                          title: const Text('Clear All Data',
                              style: TextStyle(color: Colors.red)),
                          subtitle: const Text(
                              'Delete all tracking items and events'),
                          onTap: () async {
                            final confirmed = await showDialog<bool>(
                              context: context,
                              builder: (ctx) => AlertDialog(
                                title: const Text('Clear All Data'),
                                content: const Text(
                                    'This will permanently delete all tracking items. Continue?'),
                                actions: [
                                  TextButton(
                                    onPressed: () =>
                                        Navigator.pop(ctx, false),
                                    child: const Text('Cancel'),
                                  ),
                                  FilledButton(
                                    onPressed: () =>
                                        Navigator.pop(ctx, true),
                                    style: FilledButton.styleFrom(
                                        backgroundColor: Colors.red),
                                    child: const Text('Clear All'),
                                  ),
                                ],
                              ),
                            );
                            if (confirmed == true) {
                              final db = ref.read(databaseProvider);
                              final items =
                                  await db.getAllTrackingItems();
                              for (final item in items) {
                                await db.deleteTrackingItem(item.id);
                              }
                              await ref
                                  .read(
                                      trackingItemsProvider.notifier)
                                  .loadItems();
                              if (mounted) {
                                ScaffoldMessenger.of(context)
                                    .showSnackBar(
                                  const SnackBar(
                                      content:
                                          Text('All data cleared')),
                                );
                              }
                            }
                          },
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 16),

                // About
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('About',
                            style: TextStyle(
                                fontSize: 16, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 8),
                        const ListTile(
                          leading: Icon(Icons.info_outline),
                          title: Text('eTrack v1.0.0'),
                          subtitle: Text(
                              'Privacy-first, offline-first universal tracking'),
                        ),
                        ListTile(
                          leading: const Icon(Icons.security),
                          title: const Text('Privacy'),
                          subtitle: const Text(
                              'All data stored locally. No accounts. No cloud.'),
                          onTap: () {},
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 32),
              ],
            ),
    );
  }
}
