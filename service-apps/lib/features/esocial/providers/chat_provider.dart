import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../services/chat_service.dart';

final chatServiceProvider = Provider<ChatService>((ref) {
  return ChatService();
});
