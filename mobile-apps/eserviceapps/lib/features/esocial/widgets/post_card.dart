import 'package:flutter/material.dart';
import '../../../core/models/notification_model.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../models/post_model.dart';

class PostCard extends StatelessWidget {
  final PostModel post;
  final String currentUserId;
  final VoidCallback onLike;
  final VoidCallback onComment;
  final VoidCallback onTap;

  const PostCard({
    super.key,
    required this.post,
    required this.currentUserId,
    required this.onLike,
    required this.onComment,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isLiked = post.isLikedBy(currentUserId);

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  CircleAvatar(
                    backgroundColor: AppColors.eSocialColor.withOpacity(0.1),
                    child: Text(
                      post.authorName.isNotEmpty
                          ? post.authorName[0].toUpperCase()
                          : '?',
                      style: const TextStyle(
                        color: AppColors.eSocialColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          post.authorName,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        Text(
                          AppDateUtils.timeAgo(post.createdAt),
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(post.content, style: const TextStyle(fontSize: 15)),
              if (post.imageUrl != null) ...[
                const SizedBox(height: 12),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.network(
                    post.imageUrl!,
                    width: double.infinity,
                    height: 200,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => Container(
                      height: 200,
                      color: Colors.grey[200],
                      child: const Icon(Icons.broken_image, size: 48),
                    ),
                  ),
                ),
              ],
              const SizedBox(height: 12),
              Row(
                children: [
                  InkWell(
                    onTap: onLike,
                    child: Row(
                      children: [
                        Icon(
                          isLiked ? Icons.favorite : Icons.favorite_border,
                          color: isLiked ? Colors.red : Colors.grey,
                          size: 20,
                        ),
                        const SizedBox(width: 4),
                        Text('${post.likes.length}'),
                      ],
                    ),
                  ),
                  const SizedBox(width: 24),
                  InkWell(
                    onTap: onComment,
                    child: Row(
                      children: [
                        const Icon(Icons.comment_outlined,
                            color: Colors.grey, size: 20),
                        const SizedBox(width: 4),
                        Text('${post.commentCount}'),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
