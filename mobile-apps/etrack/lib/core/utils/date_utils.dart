import 'package:intl/intl.dart';
import 'package:timeago/timeago.dart' as timeago;

class AppDateUtils {
  AppDateUtils._();

  static String formatDateTime(DateTime dt) {
    return DateFormat('MMM d, yyyy h:mm a').format(dt);
  }

  static String formatDate(DateTime dt) {
    return DateFormat('MMM d, yyyy').format(dt);
  }

  static String formatTime(DateTime dt) {
    return DateFormat('h:mm a').format(dt);
  }

  static String timeAgo(DateTime dt) {
    return timeago.format(dt, allowFromNow: true);
  }

  static String formatRelative(DateTime dt) {
    final now = DateTime.now();
    final diff = dt.difference(now);
    if (diff.isNegative) {
      return timeago.format(dt);
    }
    if (diff.inDays == 0) return 'Today';
    if (diff.inDays == 1) return 'Tomorrow';
    if (diff.inDays < 7) return 'In ${diff.inDays} days';
    return formatDate(dt);
  }
}
