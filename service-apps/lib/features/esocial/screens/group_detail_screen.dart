import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/loading_widget.dart';
import '../models/post_model.dart';
import 'groups_screen.dart';

final groupPostsProvider = StreamProvider.family<List<PostModel>, String>((
  ref,
  groupId,
) {
  return ref.watch(groupServiceProvider).getGroupPosts(groupId);
});

class GroupDetailScreen extends ConsumerStatefulWidget {
  final String groupId;
  const GroupDetailScreen({super.key, required this.groupId});
  @override
  ConsumerState<GroupDetailScreen> createState() => _GroupDetailScreenState();
}

class _GroupDetailScreenState extends ConsumerState<GroupDetailScreen> {
  final _postController = TextEditingController();

  @override
  void dispose() {
    _postController.dispose();
    super.dispose();
  }

  Future<void> _createPost() async {
    if (_postController.text.trim().isEmpty) return;
    final user = ref.read(currentUserProvider).value;
    if (user == null) return;
    await ref
        .read(groupServiceProvider)
        .createGroupPost(
          groupId: widget.groupId,
          authorId: user.uid,
          authorName: user.displayName,
          content: _postController.text.trim(),
        );
    _postController.clear();
  }

  @override
  Widget build(BuildContext context) {
    final posts = ref.watch(groupPostsProvider(widget.groupId));
    return Scaffold(
      appBar: AppBar(title: const Text('Group')),
      body: Column(
        children: [
          Expanded(
            child: posts.when(
              data: (list) {
                if (list.isEmpty)
                  return const Center(
                    child: Text('No posts in this group yet'),
                  );
                return ListView.builder(
                  itemCount: list.length,
                  itemBuilder: (ctx, i) {
                    final p = list[i];
                    return Card(
                      margin: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 4,
                      ),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: AppColors.eSocialColor.withOpacity(
                            0.1,
                          ),
                          child: Text(
                            p.authorName.isNotEmpty
                                ? p.authorName[0].toUpperCase()
                                : '?',
                            style: const TextStyle(
                              color: AppColors.eSocialColor,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        title: Text(
                          p.authorName,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                        subtitle: Text(p.content),
                      ),
                    );
                  },
                );
              },
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
                    controller: _postController,
                    decoration: const InputDecoration(
                      hintText: 'Post to group...',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 10,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: _createPost,
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
