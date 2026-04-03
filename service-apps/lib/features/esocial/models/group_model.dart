import 'package:cloud_firestore/cloud_firestore.dart';

class GroupModel {
  final String id;
  final String name;
  final String description;
  final String photoUrl;
  final String creatorId;
  final List<String> members;
  final DateTime createdAt;

  const GroupModel({
    required this.id,
    required this.name,
    this.description = '',
    this.photoUrl = '',
    required this.creatorId,
    this.members = const [],
    required this.createdAt,
  });

  factory GroupModel.fromMap(Map<String, dynamic> map, String id) {
    return GroupModel(
      id: id,
      name: map['name'] ?? '',
      description: map['description'] ?? '',
      photoUrl: map['photoUrl'] ?? '',
      creatorId: map['creatorId'] ?? '',
      members: List<String>.from(map['members'] ?? []),
      createdAt: (map['createdAt'] as Timestamp?)?.toDate() ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toMap() => {
    'name': name,
    'description': description,
    'photoUrl': photoUrl,
    'creatorId': creatorId,
    'members': members,
    'createdAt': FieldValue.serverTimestamp(),
  };
}
