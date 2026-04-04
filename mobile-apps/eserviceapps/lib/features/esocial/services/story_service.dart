import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../core/constants/app_constants.dart';
import '../models/story_model.dart';

class StoryService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Stream<List<StoryModel>> getActiveStories() {
    return _firestore
        .collection(AppConstants.storiesCollection)
        .where('expiresAt', isGreaterThan: Timestamp.now())
        .orderBy('expiresAt', descending: false)
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map(
          (s) => s.docs.map((d) => StoryModel.fromMap(d.data(), d.id)).toList(),
        );
  }

  Future<String> createStory({
    required String authorId,
    required String authorName,
    String authorPhotoUrl = '',
    required String mediaUrl,
    StoryType type = StoryType.image,
    String caption = '',
  }) async {
    final ref = await _firestore
        .collection(AppConstants.storiesCollection)
        .add({
          'authorId': authorId,
          'authorName': authorName,
          'authorPhotoUrl': authorPhotoUrl,
          'mediaUrl': mediaUrl,
          'type': type.name,
          'caption': caption,
          'expiresAt': Timestamp.fromDate(
            DateTime.now().add(const Duration(hours: 24)),
          ),
          'createdAt': FieldValue.serverTimestamp(),
          'viewedBy': [],
        });
    return ref.id;
  }

  Future<void> markViewed(String storyId, String userId) async {
    await _firestore
        .collection(AppConstants.storiesCollection)
        .doc(storyId)
        .update({
          'viewedBy': FieldValue.arrayUnion([userId]),
        });
  }
}
