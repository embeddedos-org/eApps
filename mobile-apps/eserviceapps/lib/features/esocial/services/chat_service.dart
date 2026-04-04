import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../core/constants/app_constants.dart';
import '../models/chat_model.dart';

class ChatService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Stream<List<ChatModel>> getUserChats(String userId) {
    return _firestore
        .collection(AppConstants.chatsCollection)
        .where('participants', arrayContains: userId)
        .orderBy('updatedAt', descending: true)
        .snapshots()
        .map((s) => s.docs.map((d) => ChatModel.fromMap(d.data(), d.id)).toList());
  }

  Future<String> getOrCreateChat(String userId, String otherUserId) async {
    final existing = await _firestore
        .collection(AppConstants.chatsCollection)
        .where('participants', arrayContains: userId)
        .get();

    for (final doc in existing.docs) {
      final participants = List<String>.from(doc.data()['participants'] ?? []);
      if (participants.contains(otherUserId)) return doc.id;
    }

    final ref = await _firestore.collection(AppConstants.chatsCollection).add({
      'participants': [userId, otherUserId],
      'lastMessage': '',
      'lastSenderId': '',
      'updatedAt': FieldValue.serverTimestamp(),
    });
    return ref.id;
  }

  Stream<List<MessageModel>> getMessages(String chatId) {
    return _firestore
        .collection(AppConstants.chatsCollection)
        .doc(chatId)
        .collection(AppConstants.messagesCollection)
        .orderBy('createdAt', descending: false)
        .limit(100)
        .snapshots()
        .map((s) => s.docs.map((d) => MessageModel.fromMap(d.data(), d.id)).toList());
  }

  Future<void> sendMessage({
    required String chatId,
    required String senderId,
    required String senderName,
    required String content,
    MessageType type = MessageType.text,
  }) async {
    final batch = _firestore.batch();
    final msgRef = _firestore.collection(AppConstants.chatsCollection)
        .doc(chatId).collection(AppConstants.messagesCollection).doc();
    batch.set(msgRef, {
      'chatId': chatId, 'senderId': senderId, 'senderName': senderName,
      'content': content, 'type': type.name, 'createdAt': FieldValue.serverTimestamp(),
    });
    final chatRef = _firestore.collection(AppConstants.chatsCollection).doc(chatId);
    batch.update(chatRef, {
      'lastMessage': content, 'lastSenderId': senderId,
      'updatedAt': FieldValue.serverTimestamp(),
    });
    await batch.commit();
  }
}
