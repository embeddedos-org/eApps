import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/post_model.dart';
import '../models/comment_model.dart';
import '../services/social_service.dart';

final socialServiceProvider = Provider<SocialService>((ref) => SocialService());

final feedProvider = StreamProvider<List<PostModel>>((ref) {
  return ref.watch(socialServiceProvider).getFeed();
});

final userPostsProvider =
    StreamProvider.family<List<PostModel>, String>((ref, userId) {
  return ref.watch(socialServiceProvider).getUserPosts(userId);
});

final postDetailProvider =
    FutureProvider.family<PostModel, String>((ref, postId) {
  return ref.read(socialServiceProvider).getPost(postId);
});

final commentsProvider =
    StreamProvider.family<List<CommentModel>, String>((ref, postId) {
  return ref.watch(socialServiceProvider).getComments(postId);
});
