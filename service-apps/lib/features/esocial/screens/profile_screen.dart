import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/loading_widget.dart';
import '../providers/social_provider.dart';
import '../widgets/post_card.dart';

class ProfileScreen extends ConsumerWidget {
  final String userId;
  const ProfileScreen({super.key, required this.userId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final posts = ref.watch(userPostsProvider(userId));
    final currentUser = ref.watch(currentUserProvider);
    final currentUserId = currentUser.value?.uid ?? '';

    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                CircleAvatar(
                  radius: 40,
                  backgroundColor: AppColors.eSocialColor.withOpacity(0.1),
                  child: const Icon(
                    Icons.person,
                    size: 40,
                    color: AppColors.eSocialColor,
                  ),
                ),
                const SizedBox(height: 12),
                FutureBuilder(
                  future: ref.read(authServiceProvider).getUserProfile(userId),
                  builder: (context, snapshot) {
                    return Text(
                      snapshot.data?.displayName ?? 'User',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
          const Divider(),
          Expanded(
            child: posts.when(
              data: (userPosts) {
                if (userPosts.isEmpty) {
                  return const Center(child: Text('No posts yet'));
                }
                return ListView.builder(
                  itemCount: userPosts.length,
                  itemBuilder: (context, index) => PostCard(
                    post: userPosts[index],
                    currentUserId: currentUserId,
                    onLike: () {
                      if (currentUserId.isNotEmpty) {
                        ref
                            .read(socialServiceProvider)
                            .toggleLike(userPosts[index].id, currentUserId);
                      }
                    },
                    onComment: () =>
                        context.push('/social/post/${userPosts[index].id}'),
                    onTap: () =>
                        context.push('/social/post/${userPosts[index].id}'),
                  ),
                );
              },
              loading: () => const AppLoadingWidget(),
              error: (e, _) => Center(child: Text('Error: $e')),
            ),
          ),
        ],
      ),
    );
  }
}
