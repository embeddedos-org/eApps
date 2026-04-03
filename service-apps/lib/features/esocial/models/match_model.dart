import 'package:cloud_firestore/cloud_firestore.dart';

class MatchProfile {
  final String uid;
  final String displayName;
  final String photoUrl;
  final int age;
  final String bio;
  final List<String> interests;
  final String location;

  const MatchProfile({
    required this.uid,
    required this.displayName,
    this.photoUrl = '',
    this.age = 0,
    this.bio = '',
    this.interests = const [],
    this.location = '',
  });

  factory MatchProfile.fromMap(Map<String, dynamic> map, String uid) {
    return MatchProfile(
      uid: uid,
      displayName: map['displayName'] ?? '',
      photoUrl: map['photoUrl'] ?? '',
      age: map['age'] ?? 0,
      bio: map['bio'] ?? '',
      interests: List<String>.from(map['interests'] ?? []),
      location: map['location'] ?? '',
    );
  }

  Map<String, dynamic> toMap() => {
    'displayName': displayName,
    'photoUrl': photoUrl,
    'age': age,
    'bio': bio,
    'interests': interests,
    'location': location,
  };
}

class MatchModel {
  final String id;
  final String userId;
  final String matchedUserId;
  final MatchStatus status;
  final DateTime createdAt;

  const MatchModel({
    required this.id,
    required this.userId,
    required this.matchedUserId,
    this.status = MatchStatus.pending,
    required this.createdAt,
  });

  factory MatchModel.fromMap(Map<String, dynamic> map, String id) {
    return MatchModel(
      id: id,
      userId: map['userId'] ?? '',
      matchedUserId: map['matchedUserId'] ?? '',
      status: MatchStatus.values.firstWhere(
        (e) => e.name == map['status'],
        orElse: () => MatchStatus.pending,
      ),
      createdAt: (map['createdAt'] as Timestamp?)?.toDate() ?? DateTime.now(),
    );
  }
}

enum MatchStatus { pending, matched, rejected }
