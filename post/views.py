from django.shortcuts import render
from rest_framework import viewsets, mixins

from post.models import Post, Tag, Comment, Like
from post.serializers import (
    PostSerializer,
    TagSerializer,
    PostListSerializer,
    PostDetailSerializer,
)


class TagViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    # filter_backends = [filters.SearchFilter]
    # search_fields = ["=author__username", "=tags__name"]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer

        if self.action == "retrieve":
            return PostDetailSerializer

        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
