import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';
import '../../../core/widgets/loading_widget.dart';
import '../services/chat_service.dart';
import '../models/chat_model.dart';

final chatServiceProvider = Provider<ChatService>((ref) => ChatService());
final userChatsProvider = StreamProvider<List<ChatModel>>((ref) {
  final user = ref.watch(currentUserProvider);
  return user.when(
    data: (u) => u == null ? Stream.value([]) : ref.read(chatServiceProvider).getUserChats(u.uid),
    loading: () => Stream.value([]), error: (_, __) => Stream.value([]),
  );
});

class MessagesScreen extends ConsumerWidget {
  const MessagesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final chats = ref.watch(userChatsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Messages')),
      body: chats.when(
        data: (list) {
          if (list.isEmpty) return const Center(child: Column(mainAxisSize: MainAxisSize.min,
            children: [Icon(Icons.chat_bubble_outline, size: 64, color: AppColors.textSecondary),
              SizedBox(height: 16), Text('No conversations yet')]));
          return ListView.builder(itemCount: list.length, itemBuilder: (ctx, i) {
            final chat = list[i];
            return ListTile(
              leading: CircleAvatar(backgroundColor: AppColors.eSocialColor.withOpacity(0.1),
                child: const Icon(Icons.person, color: AppColors.eSocialColor)),
              title: Text('Chat ${chat.id.substring(0, 6)}'),
              subtitle: Text(chat.lastMessage, maxLines: 1, overflow: TextOverflow.ellipsis),
              trailing: Text(AppDateUtils.timeAgo(chat.updatedAt), style: const TextStyle(fontSize: 11)),
              onTap: () => context.push('/social/chat/${chat.id}'),
            );
          });
        },
        loading: () => const AppLoadingWidget(),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }
}
