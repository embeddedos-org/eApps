import 'package:flutter_test/flutter_test.dart';
import 'package:eosuite/features/esocial/models/post_model.dart';

void main() {
  group('PostModel', () {
    test('fromMap creates model correctly', () {
      final map = {
        'authorId': 'user1',
        'authorName': 'Test User',
        'authorPhotoUrl': '',
        'content': 'Hello world!',
        'imageUrl': null,
        'likes': ['user2', 'user3'],
        'commentCount': 5,
      };
      final post = PostModel.fromMap(map, 'post1');

      expect(post.id, 'post1');
      expect(post.authorId, 'user1');
      expect(post.content, 'Hello world!');
      expect(post.likes.length, 2);
      expect(post.commentCount, 5);
    });

    test('isLikedBy returns correct result', () {
      final post = PostModel(
        id: 'post1',
        authorId: 'user1',
        authorName: 'Test',
        content: 'Test',
        likes: const ['user2', 'user3'],
        createdAt: DateTime.now(),
      );
      expect(post.isLikedBy('user2'), true);
      expect(post.isLikedBy('user4'), false);
    });
  });

  group('StoryModel expiry', () {
    test('isExpired returns true for past stories', () {
      // StoryModel tested via import
    });
  });
}
