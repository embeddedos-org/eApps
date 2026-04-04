import 'package:cloud_firestore/cloud_firestore.dart';

class StoryModel {
  final String id;
  final String authorId;
  final String authorName;
  final String authorPhotoUrl;
  final String mediaUrl;
  final StoryType type;
  final String caption;
  final DateTime expiresAt;
  final DateTime createdAt;
  final List<String> viewedBy;

  const StoryModel({
    required this.id,
    required this.authorId,
    required this.authorName,
    this.authorPhotoUrl = '',
    required this.mediaUrl,
    this.type = StoryType.image,
    this.caption = '',
    required this.expiresAt,
    required this.createdAt,
    this.viewedBy = const [],
  });

  factory StoryModel.fromMap(Map<String, dynamic> map, String id) {
    return StoryModel(
      id: id,
      authorId: map['authorId'] ?? '',
      authorName: map['authorName'] ?? '',
      authorPhotoUrl: map['authorPhotoUrl'] ?? '',
      mediaUrl: map['mediaUrl'] ?? '',
      type: StoryType.values.firstWhere(
        (e) => e.name == map['type'],
        orElse: () => StoryType.image,
      ),
      caption: map['caption'] ?? '',
      expiresAt: (map['expiresAt'] as Timestamp?)?.toDate() ?? DateTime.now(),
      createdAt: (map['createdAt'] as Timestamp?)?.toDate() ?? DateTime.now(),
      viewedBy: List<String>.from(map['viewedBy'] ?? []),
    );
  }

  Map<String, dynamic> toMap() => {
    'authorId': authorId,
    'authorName': authorName,
    'authorPhotoUrl': authorPhotoUrl,
    'mediaUrl': mediaUrl,
    'type': type.name,
    'caption': caption,
    'expiresAt': Timestamp.fromDate(expiresAt),
    'createdAt': FieldValue.serverTimestamp(),
    'viewedBy': viewedBy,
  };

  bool get isExpired => DateTime.now().isAfter(expiresAt);
}

enum StoryType { image, video, text }
