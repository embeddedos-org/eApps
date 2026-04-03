import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/loading_widget.dart';
import '../providers/social_provider.dart';
import '../widgets/post_card.dart';

class SocialFeedScreen extends ConsumerWidget {
  const SocialFeedScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final feed = ref.watch(feedProvider);
    final user = ref.watch(currentUserProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('eSocial'),
        backgroundColor: AppColors.eSocialColor.withOpacity(0.05),
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppColors.eSocialColor,
        onPressed: () => context.push('/social/create'),
        child: const Icon(Icons.edit, color: Colors.white),
      ),
      body: feed.when(
        data: (posts) {
          if (posts.isEmpty) {
            return const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.article_outlined, size: 64, color: AppColors.textSecondary),
                  SizedBox(height: 16),
                  Text('No posts yet. Be the first!'),
                ],
              ),
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.only(top: 8, bottom: 80),
            itemCount: posts.length,
            itemBuilder: (context, index) {
              final post = posts[index];
              final currentUserId = user.value?.uid ?? '';
              return PostCard(
                post: post,
                currentUserId: currentUserId,
                onLike: () {
                  if (currentUserId.isNotEmpty) {
                    ref.read(socialServiceProvider).toggleLike(post.id, currentUserId);
                  }
                },
                onComment: () => context.push('/social/post/${post.id}'),
                onTap: () => context.push('/social/post/${post.id}'),
              );
            },
          );
        },
        loading: () => const AppLoadingWidget(),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }
}
