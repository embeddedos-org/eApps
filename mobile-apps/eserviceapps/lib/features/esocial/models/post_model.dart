import 'package:cloud_firestore/cloud_firestore.dart';

class PostModel {
  final String id;
  final String authorId;
  final String authorName;
  final String authorPhotoUrl;
  final String content;
  final String? imageUrl;
  final List<String> likes;
  final int commentCount;
  final DateTime createdAt;

  const PostModel({
    required this.id,
    required this.authorId,
    required this.authorName,
    this.authorPhotoUrl = '',
    required this.content,
    this.imageUrl,
    this.likes = const [],
    this.commentCount = 0,
    required this.createdAt,
  });

  bool isLikedBy(String userId) => likes.contains(userId);

  factory PostModel.fromMap(Map<String, dynamic> map, String id) {
    return PostModel(
      id: id,
      authorId: map['authorId'] ?? '',
      authorName: map['authorName'] ?? '',
      authorPhotoUrl: map['authorPhotoUrl'] ?? '',
      content: map['content'] ?? '',
      imageUrl: map['imageUrl'],
      likes: List<String>.from(map['likes'] ?? []),
      commentCount: map['commentCount'] ?? 0,
      createdAt: (map['createdAt'] as Timestamp?)?.toDate() ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'authorId': authorId,
      'authorName': authorName,
      'authorPhotoUrl': authorPhotoUrl,
      'content': content,
      'imageUrl': imageUrl,
      'likes': likes,
      'commentCount': commentCount,
      'createdAt': FieldValue.serverTimestamp(),
    };
  }
}
