import 'package:flutter/material.dart';
import '../../../core/models/notification_model.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/date_utils.dart';

class NotificationTile extends StatelessWidget {
  final NotificationModel notification;
  final VoidCallback? onTap;

  const NotificationTile({
    super.key,
    required this.notification,
    this.onTap,
  });

  IconData _getIcon() {
    switch (notification.type) {
      case NotificationType.social:
        return Icons.people;
      case NotificationType.ride:
        return Icons.local_taxi;
      case NotificationType.travel:
        return Icons.flight;
      case NotificationType.delivery:
        return Icons.local_shipping;
      case NotificationType.wallet:
        return Icons.account_balance_wallet;
      case NotificationType.general:
        return Icons.notifications;
    }
  }

  Color _getColor() {
    switch (notification.type) {
      case NotificationType.social:
        return AppColors.eSocialColor;
      case NotificationType.ride:
        return AppColors.eRideColor;
      case NotificationType.travel:
        return AppColors.eTravelColor;
      case NotificationType.delivery:
        return AppColors.eTrackColor;
      case NotificationType.wallet:
        return AppColors.primary;
      case NotificationType.general:
        return AppColors.textSecondary;
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListTile(
      onTap: onTap,
      tileColor: notification.isRead ? null : AppColors.primary.withOpacity(0.05),
      leading: CircleAvatar(
        backgroundColor: _getColor().withOpacity(0.1),
        child: Icon(_getIcon(), color: _getColor()),
      ),
      title: Text(
        notification.title,
        style: TextStyle(
          fontWeight: notification.isRead ? FontWeight.normal : FontWeight.bold,
        ),
      ),
      subtitle: Text(notification.body, maxLines: 2, overflow: TextOverflow.ellipsis),
      trailing: Text(
        AppDateUtils.timeAgo(notification.createdAt),
        style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
      ),
    );
  }
}
