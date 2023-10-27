from django.db.models import Q
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from post.models import Post, Tag, Comment, Like
from post.serializers import (
    PostSerializer,
    TagSerializer,
    PostListSerializer,
    PostDetailSerializer,
)
from post.permissions import IsAuthorOrReadOnly


class TagViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


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


class LikeUnlikePost(APIView):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        user = request.user
        if Like.objects.filter(user=user, post=post).exists():
            Like.objects.filter(user=user, post=post).delete()
            return Response("You unliked this post")
        post.likes.add(Like.objects.create(user=user, post=post))
        return Response("You liked this post")
