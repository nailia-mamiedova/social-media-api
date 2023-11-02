from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.request import Request
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from post.models import Post, Like, Tag, Comment
from post.serializers import (
    PostListSerializer,
    PostDetailSerializer,
    TagSerializer,
    CommentSerializer,
)

POST_URL = reverse("post:post-list")


def detail_url(post_id):
    return reverse("post:post-detail", args=[post_id])


def sample_post(**params):
    defaults = {"title": "Post", "content": "Content"}
    defaults.update(params)

    return Post.objects.create(**defaults)


def sample_tag(**params):
    defaults = {"name": "Tag"}
    defaults.update(params)

    return Tag.objects.create(**defaults)


class UnauthenticatedPostApiTests(APITestCase):
    def test_auth_required(self):
        res = self.client.get(POST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPostApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@gmail.com",
            username="username",
            password="secret_password",
        )
        self.client.force_authenticate(self.user)
        self.factory = APIRequestFactory()

    def test_list_posts(self):
        sample_post(author=self.user)
        sample_post(author=self.user)

        request = self.factory.get(POST_URL)
        response = self.client.get(POST_URL)

        posts = Post.objects.all().order_by("-id")
        serializer = PostListSerializer(
            posts, many=True, context={"request": Request(request)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_post(self):
        post_data = {"title": "Post", "content": "Content"}

        response = self.client.post(POST_URL, post_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_post_detail(self):
        post = sample_post(author=self.user)

        url = detail_url(post.id)

        request = self.factory.get(url)
        response = self.client.get(url)

        serializer = PostDetailSerializer(instance=post, context={"request": request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_post(self):
        post = sample_post(author=self.user)
        post_data = {"title": "Post", "content": "Content"}

        url = detail_url(post.id)

        response = self.client.put(url, post_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_post(self):
        post = sample_post(author=self.user)
        post_data = {"title": "Post"}

        url = detail_url(post.id)

        response = self.client.patch(url, post_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_post(self):
        post = sample_post(author=self.user)

        url = detail_url(post.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # TODO: Add tests for interacting with the posts of other users

    def test_list_liked_posts(self):
        user = get_user_model().objects.create_user(
            email="someuser@gmail.com",
            username="someuser",
            password="secret_password",
        )
        post = sample_post(author=user)
        post.likes.add(Like.objects.create(user=self.user, post=post))

        url = reverse("post:liked-posts")

        response = self.client.get(url)
        request = self.factory.get(url)

        serializer = PostListSerializer(instance=post, context={"request": request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0], serializer.data)

    def test_list_tags(self):
        sample_tag()
        sample_tag()

        url = reverse("post:tag-list")

        response = self.client.get(url)

        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tag_create(self):
        tag_data = {"name": "Tag"}

        url = reverse("post:tag-list")

        response = self.client.post(url, tag_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in tag_data.keys():
            self.assertEqual(response.data[key], tag_data[key])

    def test_like_post(self):
        post = sample_post(author=self.user)

        url = reverse("post:like-unlike", args=[post.id])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "You liked this post")

    def test_commit_post(self):
        post = sample_post(author=self.user)
        comment_data = {"text": "Comment"}

        url = reverse("post:comment", args=[post.id])

        response = self.client.post(url, comment_data)

        comment = Comment.objects.get(post=post)
        serializer = CommentSerializer(comment, many=False)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], serializer.data["text"])
