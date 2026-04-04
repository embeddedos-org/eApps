import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/models/tracking_enums.dart';
import '../../../core/models/tracking_event.dart';
import '../../../core/providers/providers.dart';
import '../../../core/utils/date_utils.dart';
import '../../../core/widgets/status_badge.dart';
import '../../../core/widgets/carrier_icon.dart';
import '../../../core/widgets/timeline_widget.dart';
import 'package:uuid/uuid.dart';

class TrackingDetailScreen extends ConsumerStatefulWidget {
  final String trackingId;

  const TrackingDetailScreen({super.key, required this.trackingId});

  @override
  ConsumerState<TrackingDetailScreen> createState() =>
      _TrackingDetailScreenState();
}

class _TrackingDetailScreenState extends ConsumerState<TrackingDetailScreen> {
  bool _isRefreshing = false;

  Future<void> _refreshTracking() async {
    final db = ref.read(databaseProvider);
    final item = await db.getTrackingItemById(widget.trackingId);
    if (item == null) return;

    setState(() => _isRefreshing = true);

    final api = ref.read(trackingApiProvider);
    final result = await api.fetchTracking(item.trackingNumber, item.carrier);

    if (result.success && result.events.isNotEmpty) {
      await db.deleteEventsForItem(item.id);

      final events = result.events
          .map((e) => e.copyWith(trackingItemId: item.id))
          .toList();
      await db.insertTrackingEvents(events);

      final statusEngine = ref.read(statusEngineProvider);
      final explanation = statusEngine.explain(result.statusDescription);

      final updated = item.copyWith(
        status: result.status,
        statusExplanation: explanation.plain,
        estimatedDelivery: result.estimatedDelivery ?? item.estimatedDelivery,
        lastRefreshed: DateTime.now(),
        updatedAt: DateTime.now(),
      );
      await db.updateTrackingItem(updated);
      await ref.read(trackingItemsProvider.notifier).loadItems();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Tracking updated')),
        );
      }
    } else if (!result.success) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(result.error ?? 'Failed to refresh')),
        );
      }
    }

    setState(() => _isRefreshing = false);
  }

  Future<void> _deleteTracking() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Tracking'),
        content: const Text(
            'Are you sure you want to delete this tracking item? This cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: FilledButton.styleFrom(
                backgroundColor: Theme.of(ctx).colorScheme.error),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      await ref
          .read(trackingItemsProvider.notifier)
          .deleteItem(widget.trackingId);
      if (mounted) context.pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final itemsAsync = ref.watch(trackingItemsProvider);

    return itemsAsync.when(
      loading: () => const Scaffold(
          body: Center(child: CircularProgressIndicator())),
      error: (e, _) =>
          Scaffold(body: Center(child: Text('Error: $e'))),
      data: (items) {
        final item = items.where((i) => i.id == widget.trackingId).firstOrNull;
        if (item == null) {
          return Scaffold(
            appBar: AppBar(),
            body: const Center(child: Text('Tracking item not found')),
          );
        }

        final etaPredictor = ref.read(etaPredictorProvider);
        final eta = etaPredictor.predict(
            item.carrier, item.status, item.events.isNotEmpty
                ? item.events.last.timestamp
                : item.createdAt);

        return Scaffold(
          appBar: AppBar(
            title: Text(item.label.isNotEmpty
                ? item.label
                : item.carrier.label),
            actions: [
              IconButton(
                icon: _isRefreshing
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child:
                            CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.refresh),
                onPressed: _isRefreshing ? null : _refreshTracking,
                tooltip: 'Refresh from carrier',
              ),
              PopupMenuButton<String>(
                onSelected: (value) {
                  if (value == 'delete') _deleteTracking();
                  if (value == 'copy') {
                    Clipboard.setData(
                        ClipboardData(text: item.trackingNumber));
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                          content: Text('Tracking number copied')),
                    );
                  }
                },
                itemBuilder: (_) => [
                  const PopupMenuItem(
                      value: 'copy', child: Text('Copy Number')),
                  const PopupMenuItem(
                    value: 'delete',
                    child: Text('Delete',
                        style: TextStyle(color: Colors.red)),
                  ),
                ],
              ),
            ],
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header Card
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            CarrierIcon(
                                carrier: item.carrier, size: 32),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment:
                                    CrossAxisAlignment.start,
                                children: [
                                  Text(item.carrier.fullName,
                                      style: const TextStyle(
                                          fontWeight: FontWeight.w600,
                                          fontSize: 16)),
                                  const SizedBox(height: 4),
                                  GestureDetector(
                                    onTap: () {
                                      Clipboard.setData(ClipboardData(
                                          text: item.trackingNumber));
                                      ScaffoldMessenger.of(context)
                                          .showSnackBar(const SnackBar(
                                              content: Text(
                                                  'Copied')));
                                    },
                                    child: Row(
                                      children: [
                                        Icon(Icons.qr_code,
                                            size: 16,
                                            color: Colors.grey[600]),
                                        const SizedBox(width: 4),
                                        Flexible(
                                          child: Text(
                                            item.trackingNumber,
                                            style: TextStyle(
                                              fontFamily: 'monospace',
                                              fontSize: 14,
                                              color: Colors.grey[700],
                                            ),
                                          ),
                                        ),
                                        const SizedBox(width: 4),
                                        Icon(Icons.copy,
                                            size: 14,
                                            color: Colors.grey[500]),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            StatusBadge(status: item.status),
                            const SizedBox(width: 8),
                            Chip(
                              avatar: Icon(item.trackingType.icon,
                                  size: 16),
                              label: Text(item.trackingType.label,
                                  style:
                                      const TextStyle(fontSize: 12)),
                              visualDensity: VisualDensity.compact,
                            ),
                          ],
                        ),
                        if (item.statusExplanation.isNotEmpty) ...[
                          const SizedBox(height: 8),
                          Text(
                            item.statusExplanation,
                            style: TextStyle(
                                color: Colors.grey[700], fontSize: 14),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),

                // ETA Section
                if (eta.description.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        children: [
                          const Icon(Icons.schedule, size: 20),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Column(
                              crossAxisAlignment:
                                  CrossAxisAlignment.start,
                              children: [
                                const Text('Estimated Delivery',
                                    style: TextStyle(
                                        fontWeight: FontWeight.w500,
                                        fontSize: 13)),
                                Text(
                                  eta.estimatedDate != null
                                      ? AppDateUtils.formatRelative(
                                          eta.estimatedDate!)
                                      : eta.description,
                                  style: const TextStyle(fontSize: 15),
                                ),
                                if (eta.estimatedDate != null)
                                  Text(eta.description,
                                      style: TextStyle(
                                          fontSize: 12,
                                          color: Colors.grey[500])),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],

                // Timeline
                const SizedBox(height: 16),
                const Text('Tracking Timeline',
                    style: TextStyle(
                        fontSize: 16, fontWeight: FontWeight.w600)),
                const SizedBox(height: 8),
                TimelineWidget(events: item.events),

                // Last refreshed
                if (item.lastRefreshed != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    'Last refreshed: ${AppDateUtils.timeAgo(item.lastRefreshed!)}',
                    style: TextStyle(
                        fontSize: 12, color: Colors.grey[500]),
                    textAlign: TextAlign.center,
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }
}
