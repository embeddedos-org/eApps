import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../core/constants/app_constants.dart';
import '../models/post_model.dart';
import '../models/comment_model.dart';

class SocialService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Stream<List<PostModel>> getFeed() {
    return _firestore
        .collection(AppConstants.postsCollection)
        .orderBy('createdAt', descending: true)
        .limit(50)
        .snapshots()
        .map(
          (snapshot) => snapshot.docs
              .map((doc) => PostModel.fromMap(doc.data(), doc.id))
              .toList(),
        );
  }

  Stream<List<PostModel>> getUserPosts(String userId) {
    return _firestore
        .collection(AppConstants.postsCollection)
        .where('authorId', isEqualTo: userId)
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map(
          (snapshot) => snapshot.docs
              .map((doc) => PostModel.fromMap(doc.data(), doc.id))
              .toList(),
        );
  }

  Future<PostModel> getPost(String postId) async {
    final doc = await _firestore
        .collection(AppConstants.postsCollection)
        .doc(postId)
        .get();
    return PostModel.fromMap(doc.data()!, doc.id);
  }

  Future<String> createPost({
    required String authorId,
    required String authorName,
    String authorPhotoUrl = '',
    required String content,
    String? imageUrl,
  }) async {
    final ref = await _firestore.collection(AppConstants.postsCollection).add({
      'authorId': authorId,
      'authorName': authorName,
      'authorPhotoUrl': authorPhotoUrl,
      'content': content,
      'imageUrl': imageUrl,
      'likes': [],
      'commentCount': 0,
      'createdAt': FieldValue.serverTimestamp(),
    });
    return ref.id;
  }

  Future<void> toggleLike(String postId, String userId) async {
    final ref = _firestore.collection(AppConstants.postsCollection).doc(postId);
    final doc = await ref.get();
    final likes = List<String>.from(doc.data()?['likes'] ?? []);

    if (likes.contains(userId)) {
      likes.remove(userId);
    } else {
      likes.add(userId);
    }
    await ref.update({'likes': likes});
  }

  Stream<List<CommentModel>> getComments(String postId) {
    return _firestore
        .collection(AppConstants.postsCollection)
        .doc(postId)
        .collection(AppConstants.commentsCollection)
        .orderBy('createdAt', descending: false)
        .snapshots()
        .map(
          (snapshot) => snapshot.docs
              .map((doc) => CommentModel.fromMap(doc.data(), doc.id))
              .toList(),
        );
  }

  Future<void> addComment({
    required String postId,
    required String authorId,
    required String authorName,
    String authorPhotoUrl = '',
    required String content,
  }) async {
    final batch = _firestore.batch();

    final commentRef = _firestore
        .collection(AppConstants.postsCollection)
        .doc(postId)
        .collection(AppConstants.commentsCollection)
        .doc();

    batch.set(commentRef, {
      'postId': postId,
      'authorId': authorId,
      'authorName': authorName,
      'authorPhotoUrl': authorPhotoUrl,
      'content': content,
      'createdAt': FieldValue.serverTimestamp(),
    });

    final postRef = _firestore
        .collection(AppConstants.postsCollection)
        .doc(postId);
    batch.update(postRef, {'commentCount': FieldValue.increment(1)});

    await batch.commit();
  }

  Future<void> deletePost(String postId) async {
    await _firestore
        .collection(AppConstants.postsCollection)
        .doc(postId)
        .delete();
  }
}
