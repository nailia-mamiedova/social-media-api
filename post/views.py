from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework import viewsets, mixins, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from post.models import Post, Tag, Like
from post.serializers import (
    PostSerializer,
    TagSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
    LikeSerializer,
)
from post.permissions import IsAuthorOrReadOnly


@extend_schema_view(
    list=extend_schema(description="Display all tags"),
    create=extend_schema(description="Create new tag"),
)
class TagViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


@extend_schema_view(
    list=extend_schema(description="Display all posts by all users"),
    create=extend_schema(description="Create new post"),
    retrieve=extend_schema(description="Display post with comments and likes"),
    update=extend_schema(
        description="Update post with the specified only if you are author"
    ),
    partial_update=extend_schema(
        description="Update post with the specified only if you are author"
    ),
    destroy=extend_schema(
        description="Delete post with the specified only if you are author"
    ),
)
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly, IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset

        tag = self.request.query_params.get("tag")
        if tag:
            queryset = queryset.filter(tags__name__icontains=tag)

        queryset = queryset.filter(
            Q(author__followers=self.request.user) | Q(author=self.request.user)
        )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer

        if self.action == "retrieve":
            return PostDetailSerializer

        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="tag",
                description="Filter posts by tag",
                required=False,
                type=OpenApiTypes.STR,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class LikedPosts(APIView):
    @extend_schema(
        description="Display all posts liked by user",
        responses=PostListSerializer,
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        posts = Post.objects.filter(likes__user=user)
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)


@extend_schema_view(
    post=extend_schema(
        description="Like or unlike(if already liked) post with specified id",
    )
)
class LikeUnlikePost(generics.CreateAPIView):
    serializer_class = LikeSerializer

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user, post=Post.objects.get(pk=self.kwargs["pk"])
        )


@extend_schema_view(
    post=extend_schema(
        description="Add comment to post with specified id",
    )
)
class CommentPost(generics.CreateAPIView):
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user, post=Post.objects.get(pk=self.kwargs["pk"])
        )
