import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/constants/app_constants.dart';
import '../../../core/models/place_model.dart';
import '../../../core/providers/map_provider.dart';
import '../../../core/services/geocoding_service.dart';
import '../../../core/utils/distance_utils.dart';

class SearchScreen extends ConsumerStatefulWidget {
  const SearchScreen({super.key});

  @override
  ConsumerState<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends ConsumerState<SearchScreen> {
  final _searchController = TextEditingController();
  final _focusNode = FocusNode();
  Timer? _debounce;
  List<PlaceModel> _results = [];
  List<String> _recentSearches = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadRecentSearches();
    _focusNode.requestFocus();
  }

  Future<void> _loadRecentSearches() async {
    final prefs = await SharedPreferences.getInstance();
    final searches = prefs.getStringList(AppConstants.prefRecentSearches) ?? [];
    setState(() => _recentSearches = searches);
  }

  Future<void> _saveRecentSearch(String query) async {
    if (query.trim().isEmpty) return;
    final prefs = await SharedPreferences.getInstance();
    _recentSearches.remove(query);
    _recentSearches.insert(0, query);
    if (_recentSearches.length > AppConstants.maxRecentSearches) {
      _recentSearches = _recentSearches.sublist(0, AppConstants.maxRecentSearches);
    }
    await prefs.setStringList(AppConstants.prefRecentSearches, _recentSearches);
  }

  void _onSearchChanged(String query) {
    _debounce?.cancel();
    if (query.trim().isEmpty) {
      setState(() {
        _results = [];
        _isLoading = false;
      });
      return;
    }
    setState(() => _isLoading = true);
    _debounce = Timer(
      Duration(milliseconds: AppConstants.searchDebounceMs),
      () => _performSearch(query),
    );
  }

  Future<void> _performSearch(String query) async {
    final results = await GeocodingService.searchPlaces(query);
    if (mounted) {
      setState(() {
        _results = results;
        _isLoading = false;
      });
    }
  }

  void _selectPlace(PlaceModel place) {
    _saveRecentSearch(place.name);
    ref.read(selectedPlaceProvider.notifier).state = place;
    context.pop();
  }

  void _searchCategory(String category) {
    _searchController.text = category;
    _onSearchChanged(category);
  }

  @override
  void dispose() {
    _searchController.dispose();
    _focusNode.dispose();
    _debounce?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final currentPosition = ref.watch(currentPositionProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Search'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: AppColors.textPrimary,
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: TextField(
              controller: _searchController,
              focusNode: _focusNode,
              onChanged: _onSearchChanged,
              decoration: InputDecoration(
                hintText: 'Search places, addresses, cities...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          setState(() {
                            _results = [];
                            _isLoading = false;
                          });
                        },
                      )
                    : null,
              ),
            ),
          ),
          const SizedBox(height: 12),
          if (_searchController.text.isEmpty) ...[
            SizedBox(
              height: 90,
              child: ListView.separated(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                scrollDirection: Axis.horizontal,
                itemCount: AppConstants.placeCategories.length,
                separatorBuilder: (_, __) => const SizedBox(width: 12),
                itemBuilder: (context, index) {
                  final cat = AppConstants.placeCategories[index];
                  return GestureDetector(
                    onTap: () => _searchCategory(cat.name),
                    child: Column(
                      children: [
                        Container(
                          width: 56,
                          height: 56,
                          decoration: BoxDecoration(
                            color: AppColors.primary.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Icon(cat.icon, color: AppColors.primary),
                        ),
                        const SizedBox(height: 6),
                        Text(cat.name, style: const TextStyle(fontSize: 11)),
                      ],
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 8),
          ],
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(16),
              child: LinearProgressIndicator(color: AppColors.primary),
            ),
          Expanded(
            child: _searchController.text.isNotEmpty
                ? _results.isEmpty && !_isLoading
                    ? Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.search_off, size: 64, color: Colors.grey.shade400),
                            const SizedBox(height: 16),
                            Text('No results found',
                                style: TextStyle(fontSize: 16, color: Colors.grey.shade600)),
                          ],
                        ),
                      )
                    : ListView.separated(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        itemCount: _results.length,
                        separatorBuilder: (_, __) => const Divider(height: 1),
                        itemBuilder: (context, index) {
                          final place = _results[index];
                          String? distanceText;
                          if (currentPosition != null) {
                            final dist = DistanceUtils.haversine(
                              currentPosition,
                              LatLng(place.lat, place.lng),
                            );
                            distanceText = DistanceUtils.formatDistance(dist);
                          }
                          return ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: CircleAvatar(
                              backgroundColor: AppColors.primary.withOpacity(0.1),
                              child: const Icon(Icons.place, color: AppColors.primary),
                            ),
                            title: Text(place.name,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(fontWeight: FontWeight.w600)),
                            subtitle: Text(place.address,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(fontSize: 12)),
                            trailing: distanceText != null
                                ? Text(distanceText,
                                    style: const TextStyle(
                                        color: AppColors.primary,
                                        fontWeight: FontWeight.w500,
                                        fontSize: 12))
                                : null,
                            onTap: () => _selectPlace(place),
                          );
                        },
                      )
                : _recentSearches.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.history, size: 64, color: Colors.grey.shade400),
                            const SizedBox(height: 16),
                            Text('No recent searches',
                                style: TextStyle(fontSize: 16, color: Colors.grey.shade600)),
                          ],
                        ),
                      )
                    : ListView(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        children: [
                          Padding(
                            padding: const EdgeInsets.symmetric(vertical: 8),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Text('Recent Searches',
                                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                                TextButton(
                                  onPressed: () async {
                                    final prefs = await SharedPreferences.getInstance();
                                    await prefs.remove(AppConstants.prefRecentSearches);
                                    setState(() => _recentSearches = []);
                                  },
                                  child: const Text('Clear All'),
                                ),
                              ],
                            ),
                          ),
                          ..._recentSearches.map((search) => ListTile(
                                contentPadding: EdgeInsets.zero,
                                leading: const Icon(Icons.history, color: AppColors.textSecondary),
                                title: Text(search),
                                onTap: () {
                                  _searchController.text = search;
                                  _onSearchChanged(search);
                                },
                              )),
                        ],
                      ),
          ),
        ],
      ),
    );
  }
}
