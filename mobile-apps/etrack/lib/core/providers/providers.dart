import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../constants/app_constants.dart';
import '../database/database_helper.dart';
import '../models/tracking_item.dart';
import '../models/tracking_enums.dart';
import '../services/carrier_detector.dart';
import '../services/status_engine.dart';
import '../services/eta_predictor.dart';
import '../services/api/tracking_api_orchestrator.dart';

final databaseProvider = Provider<DatabaseHelper>((_) => DatabaseHelper.instance);
final carrierDetectorProvider = Provider<CarrierDetector>((_) => CarrierDetector());
final statusEngineProvider = Provider<StatusEngine>((_) => StatusEngine());
final etaPredictorProvider = Provider<EtaPredictor>((_) => EtaPredictor());
final trackingApiProvider = Provider<TrackingApiOrchestrator>((_) => TrackingApiOrchestrator());

final themeModeProvider = StateNotifierProvider<ThemeModeNotifier, ThemeMode>(
  (_) => ThemeModeNotifier(),
);

class ThemeModeNotifier extends StateNotifier<ThemeMode> {
  ThemeModeNotifier() : super(ThemeMode.system) {
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final value = prefs.getString(AppConstants.keyThemeMode);
    if (value == 'light') state = ThemeMode.light;
    else if (value == 'dark') state = ThemeMode.dark;
    else state = ThemeMode.system;
  }

  Future<void> setThemeMode(ThemeMode mode) async {
    state = mode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.keyThemeMode, mode.name);
  }
}

final trackingItemsProvider =
    StateNotifierProvider<TrackingItemsNotifier, AsyncValue<List<TrackingItem>>>(
  (ref) => TrackingItemsNotifier(ref.read(databaseProvider)),
);

class TrackingItemsNotifier extends StateNotifier<AsyncValue<List<TrackingItem>>> {
  final DatabaseHelper _db;

  TrackingItemsNotifier(this._db) : super(const AsyncValue.loading()) {
    loadItems();
  }

  Future<void> loadItems() async {
    try {
      state = const AsyncValue.loading();
      final items = await _db.getAllTrackingItems();
      state = AsyncValue.data(items);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> addItem(TrackingItem item) async {
    await _db.insertTrackingItem(item);
    await loadItems();
  }

  Future<void> updateItem(TrackingItem item) async {
    await _db.updateTrackingItem(item);
    await loadItems();
  }

  Future<void> deleteItem(String id) async {
    await _db.deleteTrackingItem(id);
    await loadItems();
  }

  Future<List<TrackingItem>> search(String query) async {
    return _db.searchTrackingItems(query);
  }
}

final searchQueryProvider = StateProvider<String>((_) => '');
final selectedTypeFilterProvider = StateProvider<TrackingType?>((_) => null);
final selectedTagFilterProvider = StateProvider<TrackingTag?>((_) => null);

final filteredTrackingProvider = Provider<List<TrackingItem>>((ref) {
  final itemsAsync = ref.watch(trackingItemsProvider);
  final query = ref.watch(searchQueryProvider);
  final typeFilter = ref.watch(selectedTypeFilterProvider);
  final tagFilter = ref.watch(selectedTagFilterProvider);

  return itemsAsync.when(
    data: (items) {
      var filtered = items;
      if (query.isNotEmpty) {
        final q = query.toLowerCase();
        filtered = filtered.where((i) =>
            i.trackingNumber.toLowerCase().contains(q) ||
            i.label.toLowerCase().contains(q) ||
            i.carrier.label.toLowerCase().contains(q)).toList();
      }
      if (typeFilter != null) {
        filtered = filtered.where((i) => i.trackingType == typeFilter).toList();
      }
      if (tagFilter != null) {
        filtered = filtered.where((i) => i.tags.contains(tagFilter)).toList();
      }
      return filtered;
    },
    loading: () => [],
    error: (_, __) => [],
  );
});
