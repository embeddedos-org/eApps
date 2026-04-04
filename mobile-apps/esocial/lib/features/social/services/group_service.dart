import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../core/constants/app_constants.dart';
import '../models/group_model.dart';
import '../models/post_model.dart';

class GroupService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Stream<List<GroupModel>> getUserGroups(String userId) {
    return _firestore
        .collection(AppConstants.firestoreGroupsCollection)
        .where('memberIds', arrayContains: userId)
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map((snap) => snap.docs
            .map((doc) => GroupModel.fromMap(doc.data(), doc.id))
            .toList());
  }

  Stream<List<GroupModel>> discoverGroups() {
    return _firestore
        .collection(AppConstants.firestoreGroupsCollection)
        .where('isPublic', isEqualTo: true)
        .orderBy('createdAt', descending: true)
        .limit(50)
        .snapshots()
        .map((snap) => snap.docs
            .map((doc) => GroupModel.fromMap(doc.data(), doc.id))
            .toList());
  }

  Future<GroupModel> createGroup(GroupModel group) async {
    final doc = await _firestore
        .collection(AppConstants.firestoreGroupsCollection)
        .add(group.toMap());
    return GroupModel.fromMap(group.toMap(), doc.id);
  }

  Future<void> joinGroup(String groupId, String userId) async {
    await _firestore
        .collection(AppConstants.firestoreGroupsCollection)
        .doc(groupId)
        .update({
      'memberIds': FieldValue.arrayUnion([userId]),
    });
  }

  Future<void> leaveGroup(String groupId, String userId) async {
    await _firestore
        .collection(AppConstants.firestoreGroupsCollection)
        .doc(groupId)
        .update({
      'memberIds': FieldValue.arrayRemove([userId]),
    });
  }

  Future<void> deleteGroup(String groupId) async {
    await _firestore
        .collection(AppConstants.firestoreGroupsCollection)
        .doc(groupId)
        .delete();
  }

  Stream<List<PostModel>> getGroupPosts(String groupId) {
    return _firestore
        .collection(AppConstants.firestorePostsCollection)
        .where('groupId', isEqualTo: groupId)
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map((snap) => snap.docs
            .map((doc) => PostModel.fromMap(doc.data(), doc.id))
            .toList());
  }

  Stream<GroupModel> getGroupStream(String groupId) {
    return _firestore
        .collection(AppConstants.firestoreGroupsCollection)
        .doc(groupId)
        .snapshots()
        .map((doc) => GroupModel.fromMap(doc.data()!, doc.id));
  }
}
