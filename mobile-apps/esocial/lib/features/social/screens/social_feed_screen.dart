import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/providers/auth_provider.dart';
import '../../../../core/widgets/loading_widget.dart';
import '../../../../core/widgets/error_widget.dart';
import '../providers/social_provider.dart';
import '../widgets/post_card.dart';

class SocialFeedScreen extends ConsumerWidget {
  const SocialFeedScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(currentUserProvider).value;
    final feedAsync = ref.watch(feedPostsProvider);
    final currentUserId = user?.id ?? '';

    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: const BoxDecoration(
                gradient: AppColors.primaryGradient,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.people_alt_rounded, size: 18, color: Colors.white),
            ),
            const SizedBox(width: 8),
            const Text('eSocial'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.favorite_border_rounded),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.chat_outlined),
            onPressed: () => context.push('/messages'),
          ),
        ],
      ),
      body: feedAsync.when(
        loading: () => const LoadingWidget(message: 'Loading feed...'),
        error: (e, _) => AppErrorWidget(
          message: e.toString(),
          onRetry: () => ref.invalidate(feedPostsProvider),
        ),
        data: (posts) {
          if (posts.isEmpty) {
            return const EmptyStateWidget(
              title: 'No Posts Yet',
              subtitle: 'Follow people or create your first post!',
              icon: Icons.dynamic_feed_rounded,
            );
          }
          return RefreshIndicator(
            color: AppColors.primary,
            onRefresh: () async => ref.invalidate(feedPostsProvider),
            child: ListView.builder(
              itemCount: posts.length,
              itemBuilder: (context, index) {
                final post = posts[index];
                return PostCard(
                  post: post,
                  currentUserId: currentUserId,
                  onLike: () {
                    ref.read(socialServiceProvider).toggleLike(
                      post.id,
                      currentUserId,
                      post.isLikedBy(currentUserId),
                    );
                  },
                  onComment: () => context.push('/post/${post.id}'),
                  onTap: () => context.push('/post/${post.id}'),
                  onProfileTap: () => context.push('/profile/${post.authorId}'),
                );
              },
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/create-post'),
        child: const Icon(Icons.add_rounded),
      ),
    );
  }
}
