from rest_framework import serializers

from post.models import Tag, Post, Comment, Like


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "text", "created_at", "post", "user")


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "post", "user", "created_at")


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "title", "content", "created_at", "tags", "picture")


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    likes = serializers.IntegerField(source="likes.count")
    comments = serializers.IntegerField(source="comments.count")
    like = serializers.HyperlinkedIdentityField(
        view_name="post:like-unlike", lookup_field="pk"
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "created_at",
            "tags",
            "picture",
            "author",
            "likes",
            "comments",
            "like",
        )


class PostDetailSerializer(PostListSerializer):
    likes = serializers.StringRelatedField(many=True, read_only=True)
    comments = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="text"
    )
