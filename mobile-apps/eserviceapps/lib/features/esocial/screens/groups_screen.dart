import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/loading_widget.dart';
import '../services/group_service.dart';
import '../models/group_model.dart';

final groupServiceProvider = Provider<GroupService>((ref) => GroupService());
final userGroupsProvider = StreamProvider<List<GroupModel>>((ref) {
  final user = ref.watch(currentUserProvider);
  return user.when(
    data: (u) => u == null
        ? Stream.value([])
        : ref.read(groupServiceProvider).getUserGroups(u.uid),
    loading: () => Stream.value([]),
    error: (_, __) => Stream.value([]),
  );
});

class GroupsScreen extends ConsumerWidget {
  const GroupsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final groups = ref.watch(userGroupsProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Groups'),
        backgroundColor: AppColors.eSocialColor.withOpacity(0.05),
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppColors.eSocialColor,
        onPressed: () => _createGroup(context, ref),
        child: const Icon(Icons.group_add, color: Colors.white),
      ),
      body: groups.when(
        data: (list) {
          if (list.isEmpty)
            return const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.groups_outlined,
                    size: 64,
                    color: AppColors.textSecondary,
                  ),
                  SizedBox(height: 16),
                  Text('No groups yet'),
                ],
              ),
            );
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: list.length,
            itemBuilder: (ctx, i) {
              final g = list[i];
              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: AppColors.eSocialColor.withOpacity(0.1),
                    child: const Icon(
                      Icons.group,
                      color: AppColors.eSocialColor,
                    ),
                  ),
                  title: Text(
                    g.name,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text(
                    '${g.members.length} members${g.description.isNotEmpty ? " • ${g.description}" : ""}',
                  ),
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () => context.push('/social/groups/${g.id}'),
                ),
              );
            },
          );
        },
        loading: () => const AppLoadingWidget(),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }

  void _createGroup(BuildContext context, WidgetRef ref) {
    final nameCtrl = TextEditingController();
    final descCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Create Group'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameCtrl,
              decoration: const InputDecoration(labelText: 'Group Name'),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: descCtrl,
              decoration: const InputDecoration(
                labelText: 'Description (optional)',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () async {
              if (nameCtrl.text.trim().isEmpty) return;
              final user = ref.read(currentUserProvider).value;
              if (user == null) return;
              await ref
                  .read(groupServiceProvider)
                  .createGroup(
                    name: nameCtrl.text.trim(),
                    description: descCtrl.text.trim(),
                    creatorId: user.uid,
                  );
              if (ctx.mounted) Navigator.pop(ctx);
            },
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }
}
