import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../core/constants/app_constants.dart';
import '../models/match_model.dart';

class DatingService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Future<List<MatchProfile>> getProfiles(String currentUserId) async {
    final snapshot = await _firestore.collection(AppConstants.usersCollection)
        .where(FieldPath.documentId, isNotEqualTo: currentUserId).limit(20).get();
    return snapshot.docs.map((d) => MatchProfile.fromMap(d.data(), d.id)).toList();
  }

  Future<void> swipeRight(String userId, String targetUserId) async {
    await _firestore.collection(AppConstants.matchesCollection).add({
      'userId': userId, 'matchedUserId': targetUserId,
      'status': MatchStatus.pending.name, 'createdAt': FieldValue.serverTimestamp(),
    });
    final reverseMatch = await _firestore.collection(AppConstants.matchesCollection)
        .where('userId', isEqualTo: targetUserId)
        .where('matchedUserId', isEqualTo: userId)
        .where('status', isEqualTo: MatchStatus.pending.name).get();
    if (reverseMatch.docs.isNotEmpty) {
      for (final doc in reverseMatch.docs) {
        await doc.reference.update({'status': MatchStatus.matched.name});
      }
      final mySwipe = await _firestore.collection(AppConstants.matchesCollection)
          .where('userId', isEqualTo: userId)
          .where('matchedUserId', isEqualTo: targetUserId).get();
      for (final doc in mySwipe.docs) {
        await doc.reference.update({'status': MatchStatus.matched.name});
      }
    }
  }

  Future<void> swipeLeft(String userId, String targetUserId) async {
    await _firestore.collection(AppConstants.matchesCollection).add({
      'userId': userId, 'matchedUserId': targetUserId,
      'status': MatchStatus.rejected.name, 'createdAt': FieldValue.serverTimestamp(),
    });
  }

  Stream<List<MatchModel>> getMatches(String userId) {
    return _firestore.collection(AppConstants.matchesCollection)
        .where('userId', isEqualTo: userId)
        .where('status', isEqualTo: MatchStatus.matched.name)
        .snapshots()
        .map((s) => s.docs.map((d) => MatchModel.fromMap(d.data(), d.id)).toList());
  }
}
