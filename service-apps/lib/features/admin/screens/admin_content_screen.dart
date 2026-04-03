import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../core/constants/app_constants.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/loading_widget.dart';
import '../../../core/utils/date_utils.dart';

class AdminContentScreen extends StatelessWidget {
  const AdminContentScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Content Moderation')),
      body: StreamBuilder<QuerySnapshot>(
        stream: FirebaseFirestore.instance
            .collection(AppConstants.postsCollection)
            .orderBy('createdAt', descending: true)
            .limit(50)
            .snapshots(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting)
            return const AppLoadingWidget();
          if (!snapshot.hasData || snapshot.data!.docs.isEmpty)
            return const Center(child: Text('No content to review'));
          final posts = snapshot.data!.docs;
          return ListView.builder(
            itemCount: posts.length,
            itemBuilder: (ctx, i) {
              final p = posts[i].data() as Map<String, dynamic>;
              final createdAt =
                  (p['createdAt'] as Timestamp?)?.toDate() ?? DateTime.now();
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                child: ListTile(
                  leading: const CircleAvatar(
                    backgroundColor: Color(0xFFFFF3E0),
                    child: Icon(Icons.article, color: AppColors.warning),
                  ),
                  title: Text(
                    p['content'] ?? '',
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  subtitle: Text(
                    '${p['authorName'] ?? 'Unknown'} • ${AppDateUtils.timeAgo(createdAt)}',
                  ),
                  trailing: PopupMenuButton(
                    itemBuilder: (ctx) => [
                      const PopupMenuItem(
                        value: 'approve',
                        child: Text('Approve'),
                      ),
                      const PopupMenuItem(
                        value: 'delete',
                        child: Text(
                          'Delete',
                          style: TextStyle(color: AppColors.error),
                        ),
                      ),
                    ],
                    onSelected: (v) {
                      if (v == 'delete') posts[i].reference.delete();
                    },
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
