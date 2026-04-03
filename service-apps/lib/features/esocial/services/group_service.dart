import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../core/constants/app_constants.dart';
import '../models/group_model.dart';
import '../models/post_model.dart';

class GroupService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Stream<List<GroupModel>> getUserGroups(String userId) {
    return _firestore
        .collection(AppConstants.groupsCollection)
        .where('members', arrayContains: userId)
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map(
          (s) => s.docs.map((d) => GroupModel.fromMap(d.data(), d.id)).toList(),
        );
  }

  Future<String> createGroup({
    required String name,
    String description = '',
    required String creatorId,
  }) async {
    final ref = await _firestore.collection(AppConstants.groupsCollection).add({
      'name': name,
      'description': description,
      'photoUrl': '',
      'creatorId': creatorId,
      'members': [creatorId],
      'createdAt': FieldValue.serverTimestamp(),
    });
    return ref.id;
  }

  Future<void> joinGroup(String groupId, String userId) async {
    await _firestore
        .collection(AppConstants.groupsCollection)
        .doc(groupId)
        .update({
          'members': FieldValue.arrayUnion([userId]),
        });
  }

  Future<void> leaveGroup(String groupId, String userId) async {
    await _firestore
        .collection(AppConstants.groupsCollection)
        .doc(groupId)
        .update({
          'members': FieldValue.arrayRemove([userId]),
        });
  }

  Stream<List<PostModel>> getGroupPosts(String groupId) {
    return _firestore
        .collection(AppConstants.groupsCollection)
        .doc(groupId)
        .collection(AppConstants.postsCollection)
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map(
          (s) => s.docs.map((d) => PostModel.fromMap(d.data(), d.id)).toList(),
        );
  }

  Future<void> createGroupPost({
    required String groupId,
    required String authorId,
    required String authorName,
    required String content,
  }) async {
    await _firestore
        .collection(AppConstants.groupsCollection)
        .doc(groupId)
        .collection(AppConstants.postsCollection)
        .add({
          'authorId': authorId,
          'authorName': authorName,
          'authorPhotoUrl': '',
          'content': content,
          'imageUrl': null,
          'likes': [],
          'commentCount': 0,
          'createdAt': FieldValue.serverTimestamp(),
        });
  }
}
