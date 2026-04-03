import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../../../core/widgets/loading_widget.dart';
import '../services/story_service.dart';
import '../models/story_model.dart';

final storyServiceProvider = Provider<StoryService>((ref) => StoryService());
final storiesProvider = StreamProvider<List<StoryModel>>((ref) {
  return ref.watch(storyServiceProvider).getActiveStories();
});

class StoriesScreen extends ConsumerWidget {
  const StoriesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stories = ref.watch(storiesProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Stories'),
        backgroundColor: AppColors.eSocialColor.withOpacity(0.05),
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppColors.eSocialColor,
        onPressed: () => _createTextStory(context, ref),
        child: const Icon(Icons.add, color: Colors.white),
      ),
      body: stories.when(
        data: (list) {
          if (list.isEmpty)
            return const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.auto_stories,
                    size: 64,
                    color: AppColors.textSecondary,
                  ),
                  SizedBox(height: 16),
                  Text('No stories yet'),
                  Text('Create one!', style: TextStyle(color: Colors.grey)),
                ],
              ),
            );
          final grouped = <String, List<StoryModel>>{};
          for (final s in list) {
            grouped.putIfAbsent(s.authorId, () => []).add(s);
          }
          return ListView(
            padding: const EdgeInsets.all(16),
            children: grouped.entries.map((entry) {
              final author = entry.value.first;
              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: AppColors.eSocialColor.withOpacity(0.1),
                    child: Text(
                      author.authorName.isNotEmpty
                          ? author.authorName[0].toUpperCase()
                          : '?',
                      style: const TextStyle(
                        color: AppColors.eSocialColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  title: Text(author.authorName),
                  subtitle: Text(
                    '${entry.value.length} ${entry.value.length == 1 ? "story" : "stories"}',
                  ),
                  trailing: Text(
                    AppDateUtils.timeAgo(author.createdAt),
                    style: const TextStyle(fontSize: 11),
                  ),
                  onTap: () => _viewStory(context, ref, entry.value.first),
                ),
              );
            }).toList(),
          );
        },
        loading: () => const AppLoadingWidget(),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }

  void _viewStory(BuildContext context, WidgetRef ref, StoryModel story) {
    final userId = ref.read(currentUserProvider).value?.uid;
    if (userId != null)
      ref.read(storyServiceProvider).markViewed(story.id, userId);
    showDialog(
      context: context,
      builder: (ctx) => Dialog.fullscreen(
        child: Stack(
          children: [
            Container(
              color: AppColors.eSocialColor.withOpacity(0.9),
              child: Center(
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        story.authorName,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 24),
                      if (story.type == StoryType.text)
                        Text(
                          story.caption,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                          ),
                          textAlign: TextAlign.center,
                        )
                      else if (story.mediaUrl.isNotEmpty)
                        ClipRRect(
                          borderRadius: BorderRadius.circular(12),
                          child: Image.network(
                            story.mediaUrl,
                            height: 300,
                            fit: BoxFit.cover,
                            errorBuilder: (_, __, ___) => const Icon(
                              Icons.broken_image,
                              size: 64,
                              color: Colors.white70,
                            ),
                          ),
                        ),
                      if (story.caption.isNotEmpty &&
                          story.type != StoryType.text) ...[
                        const SizedBox(height: 16),
                        Text(
                          story.caption,
                          style: const TextStyle(
                            color: Colors.white70,
                            fontSize: 16,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                      const SizedBox(height: 16),
                      Text(
                        '${story.viewedBy.length} views',
                        style: const TextStyle(color: Colors.white54),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            Positioned(
              top: 48,
              right: 16,
              child: IconButton(
                onPressed: () => Navigator.pop(ctx),
                icon: const Icon(Icons.close, color: Colors.white, size: 32),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _createTextStory(BuildContext context, WidgetRef ref) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Create Story'),
        content: TextField(
          controller: controller,
          maxLines: 3,
          decoration: const InputDecoration(hintText: 'What\'s on your mind?'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () async {
              if (controller.text.trim().isEmpty) return;
              final user = ref.read(currentUserProvider).value;
              if (user == null) return;
              await ref
                  .read(storyServiceProvider)
                  .createStory(
                    authorId: user.uid,
                    authorName: user.displayName,
                    mediaUrl: '',
                    type: StoryType.text,
                    caption: controller.text.trim(),
                  );
              if (ctx.mounted) Navigator.pop(ctx);
            },
            child: const Text('Post'),
          ),
        ],
      ),
    );
  }
}
