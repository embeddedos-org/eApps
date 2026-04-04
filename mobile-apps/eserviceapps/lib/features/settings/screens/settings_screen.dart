import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/theme/app_colors.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(currentUserProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        children: [
          // Profile header
          user.when(
            data: (u) => Container(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 40,
                    backgroundColor: AppColors.primary.withOpacity(0.1),
                    child: Text(
                      u?.displayName.isNotEmpty == true
                          ? u!.displayName[0].toUpperCase()
                          : '?',
                      style: const TextStyle(
                        fontSize: 32,
                        color: AppColors.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    u?.displayName ?? 'User',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  Text(
                    u?.email ?? '',
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
          ),
          const Divider(),
          _SettingsTile(
            icon: Icons.person_outline,
            title: 'Edit Profile',
            onTap: () {},
          ),
          _SettingsTile(
            icon: Icons.account_balance_wallet,
            title: 'Wallet',
            onTap: () => context.push('/wallet'),
          ),
          _SettingsTile(
            icon: Icons.notifications_outlined,
            title: 'Notifications',
            onTap: () => context.push('/notifications'),
          ),
          const Divider(),
          _SettingsTile(
            icon: Icons.dark_mode_outlined,
            title: 'Dark Mode',
            trailing: Switch(
              value: Theme.of(context).brightness == Brightness.dark,
              onChanged: (_) {},
            ),
          ),
          _SettingsTile(
            icon: Icons.language,
            title: 'Language',
            subtitle: 'English',
          ),
          _SettingsTile(
            icon: Icons.security,
            title: 'Privacy & Security',
            onTap: () {},
          ),
          const Divider(),
          _SettingsTile(
            icon: Icons.admin_panel_settings,
            title: 'Admin Panel',
            onTap: () => context.push('/admin'),
          ),
          _SettingsTile(
            icon: Icons.help_outline,
            title: 'Help & Support',
            onTap: () {},
          ),
          _SettingsTile(
            icon: Icons.info_outline,
            title: 'About',
            subtitle: 'EoSuite v1.0.0',
          ),
          const Divider(),
          _SettingsTile(
            icon: Icons.logout,
            title: 'Sign Out',
            titleColor: AppColors.error,
            onTap: () {
              ref.read(authServiceProvider).signOut();
              context.go('/login');
            },
          ),
        ],
      ),
    );
  }
}

class _SettingsTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;
  final Color? titleColor;
  final Widget? trailing;
  final VoidCallback? onTap;

  const _SettingsTile({
    required this.icon,
    required this.title,
    this.subtitle,
    this.titleColor,
    this.trailing,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: titleColor ?? AppColors.textSecondary),
      title: Text(title, style: TextStyle(color: titleColor)),
      subtitle: subtitle != null ? Text(subtitle!) : null,
      trailing:
          trailing ??
          (onTap != null
              ? const Icon(Icons.arrow_forward_ios, size: 16)
              : null),
      onTap: onTap,
    );
  }
}
