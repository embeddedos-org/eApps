import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/loading_widget.dart';
import '../providers/social_provider.dart';
import '../widgets/post_card.dart';
import '../widgets/comment_tile.dart';

class PostDetailScreen extends ConsumerStatefulWidget {
  final String postId;
  const PostDetailScreen({super.key, required this.postId});

  @override
  ConsumerState<PostDetailScreen> createState() => _PostDetailScreenState();
}

class _PostDetailScreenState extends ConsumerState<PostDetailScreen> {
  final _commentController = TextEditingController();

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  Future<void> _addComment() async {
    if (_commentController.text.trim().isEmpty) return;
    final user = ref.read(currentUserProvider).value;
    if (user == null) return;

    await ref.read(socialServiceProvider).addComment(
          postId: widget.postId,
          authorId: user.uid,
          authorName: user.displayName,
          authorPhotoUrl: user.photoUrl,
          content: _commentController.text.trim(),
        );
    _commentController.clear();
  }

  @override
  Widget build(BuildContext context) {
    final post = ref.watch(postDetailProvider(widget.postId));
    final comments = ref.watch(commentsProvider(widget.postId));
    final user = ref.watch(currentUserProvider);
    final currentUserId = user.value?.uid ?? '';

    return Scaffold(
      appBar: AppBar(title: const Text('Post')),
      body: Column(
        children: [
          Expanded(
            child: post.when(
              data: (p) => SingleChildScrollView(
                child: Column(
                  children: [
                    PostCard(
                      post: p,
                      currentUserId: currentUserId,
                      onLike: () {
                        if (currentUserId.isNotEmpty) {
                          ref.read(socialServiceProvider).toggleLike(p.id, currentUserId);
                          ref.invalidate(postDetailProvider(widget.postId));
                        }
                      },
                      onComment: () {},
                      onTap: () {},
                    ),
                    const Divider(),
                    comments.when(
                      data: (cmts) => ListView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: cmts.length,
                        itemBuilder: (context, index) =>
                            CommentTile(comment: cmts[index]),
                      ),
                      loading: () => const AppLoadingWidget(),
                      error: (e, _) => Text('Error: $e'),
                    ),
                  ],
                ),
              ),
              loading: () => const AppLoadingWidget(),
              error: (e, _) => Center(child: Text('Error: $e')),
            ),
          ),
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 4,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _commentController,
                    decoration: const InputDecoration(
                      hintText: 'Write a comment...',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: _addComment,
                  icon: const Icon(Icons.send, color: AppColors.eSocialColor),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
