import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/loading_widget.dart';
import '../services/dating_service.dart';
import '../models/match_model.dart';

final datingServiceProvider = Provider<DatingService>((ref) => DatingService());

class DatingScreen extends ConsumerStatefulWidget {
  const DatingScreen({super.key});
  @override
  ConsumerState<DatingScreen> createState() => _DatingScreenState();
}

class _DatingScreenState extends ConsumerState<DatingScreen> {
  List<MatchProfile> _profiles = [];
  int _currentIndex = 0;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadProfiles();
  }

  Future<void> _loadProfiles() async {
    final user = ref.read(currentUserProvider).value;
    if (user == null) return;
    final profiles = await ref.read(datingServiceProvider).getProfiles(user.uid);
    setState(() { _profiles = profiles; _loading = false; });
  }

  Future<void> _swipe(bool right) async {
    if (_currentIndex >= _profiles.length) return;
    final user = ref.read(currentUserProvider).value;
    if (user == null) return;
    final target = _profiles[_currentIndex];
    if (right) {
      await ref.read(datingServiceProvider).swipeRight(user.uid, target.uid);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Liked ${target.displayName}!'), backgroundColor: AppColors.success));
    } else {
      await ref.read(datingServiceProvider).swipeLeft(user.uid, target.uid);
    }
    setState(() => _currentIndex++);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Dating'), backgroundColor: AppColors.eSocialColor.withOpacity(0.05)),
      body: _loading
          ? const AppLoadingWidget()
          : _currentIndex >= _profiles.length
              ? const Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
                  Icon(Icons.favorite_outline, size: 64, color: AppColors.textSecondary),
                  SizedBox(height: 16), Text('No more profiles nearby'),
                  Text('Check back later!', style: TextStyle(color: Colors.grey))]))
              : Column(children: [
                  Expanded(child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Card(
                      elevation: 4,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(24),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            CircleAvatar(radius: 60, backgroundColor: AppColors.eSocialColor.withOpacity(0.1),
                              child: Text(_profiles[_currentIndex].displayName.isNotEmpty
                                  ? _profiles[_currentIndex].displayName[0].toUpperCase() : '?',
                                style: const TextStyle(fontSize: 48, color: AppColors.eSocialColor))),
                            const SizedBox(height: 20),
                            Text(_profiles[_currentIndex].displayName,
                              style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                            if (_profiles[_currentIndex].age > 0) Text('Age: ${_profiles[_currentIndex].age}',
                              style: TextStyle(fontSize: 16, color: Colors.grey[600])),
                            const SizedBox(height: 12),
                            if (_profiles[_currentIndex].bio.isNotEmpty)
                              Text(_profiles[_currentIndex].bio, textAlign: TextAlign.center,
                                style: const TextStyle(fontSize: 15)),
                            const SizedBox(height: 12),
                            if (_profiles[_currentIndex].interests.isNotEmpty)
                              Wrap(spacing: 8, runSpacing: 4, children: _profiles[_currentIndex].interests
                                  .map((i) => Chip(label: Text(i, style: const TextStyle(fontSize: 12)),
                                    backgroundColor: AppColors.eSocialColor.withOpacity(0.1))).toList()),
                          ],
                        ),
                      ),
                    ),
                  )),
                  Padding(
                    padding: const EdgeInsets.only(bottom: 32),
                    child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                      FloatingActionButton(heroTag: 'dislike', backgroundColor: Colors.white,
                        onPressed: () => _swipe(false),
                        child: const Icon(Icons.close, color: AppColors.error, size: 32)),
                      const SizedBox(width: 32),
                      FloatingActionButton(heroTag: 'like', backgroundColor: AppColors.eSocialColor,
                        onPressed: () => _swipe(true),
                        child: const Icon(Icons.favorite, color: Colors.white, size: 32)),
                    ]),
                  ),
                ]),
    );
  }
}
