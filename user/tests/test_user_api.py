from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from user.serializers import UserListSerializer, UserDetailSerializer, UserSerializer

USER_URL = reverse("user:user-list")
USER_MANAGE_URL = reverse("user:manage")


def detail_url(user_id):
    return reverse("user:user-detail", args=[user_id])


def sample_user(email, **params):
    defaults = {
        "email": f"{email}@gmail.com",
        "username": email.split("@")[0],
        "password": "secret_password",
    }
    defaults.update(params)

    return get_user_model().objects.create_user(**defaults)


class UnauthenticatedUserApiTests(APITestCase):
    def test_user_registration(self):
        user_data = {
            "email": "test_user@gmail.com",
            "username": "test_user",
            "password": "test_password",
        }

        url = reverse("user:register")

        response = self.client.post(url, user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("password" not in response.data)


class AuthenticatedUserApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@gmail.com",
            username="username",
            password="secret_password",
        )
        self.client.force_authenticate(self.user)
        self.factory = APIRequestFactory()

    def test_user_login(self):
        url = reverse("user:login")

        response = self.client.post(
            url, {"email": "user@gmail.com", "password": "secret_password"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("token" in response.data)

    def test_user_login_invalid_credentials(self):
        url = reverse("user:login")

        response = self.client.post(
            url, {"email": "user@gmail.com", "password": "invalid_password"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Incorrect Login credentials")

    def test_user_logout(self):
        login_url = reverse("user:login")
        url = reverse("user:logout")

        self.client.post(
            login_url, {"email": "user@gmail.com", "password": "secret_password"}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "User Logged out successfully")

    def test_user_list(self):
        sample_user("test_user_1")
        sample_user("test_user_2")

        request = self.factory.get(USER_URL)
        response = self.client.get(USER_URL)

        users = get_user_model().objects.order_by("id").exclude(id=self.user.id)
        serializer = UserListSerializer(
            users, many=True, context={"request": Request(request)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_user_detail(self):
        user = sample_user("test_user")

        url = detail_url(user.id)

        request = self.factory.get(url)
        response = self.client.get(url)

        serializer = UserDetailSerializer(
            instance=user, context={"request": Request(request)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_current_user_profile(self):
        request = self.factory.get(USER_MANAGE_URL)
        response = self.client.get(USER_MANAGE_URL)

        serializer = UserSerializer(
            instance=self.user, context={"request": Request(request)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_put_current_user_profile(self):
        user_data = {
            "email": "new_email@gmail.com",
            "username": "new_username",
            "password": "new_password",
        }

        response = self.client.put(USER_MANAGE_URL, user_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], user_data["email"])
        self.assertEqual(response.data["username"], user_data["username"])
        self.assertTrue(self.user.check_password(user_data["password"]))

    def test_patch_current_user_profile(self):
        user_data = {"email": "new_email_2.0@gmail.com"}

        response = self.client.patch(USER_MANAGE_URL, user_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], user_data["email"])

    def test_delete_current_user_profile(self):
        response = self.client.delete(USER_MANAGE_URL)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(get_user_model().objects.filter(id=self.user.id).exists())

    def test_follow_user(self):
        user = sample_user("test_user")

        url = reverse("user:follow-unfollow", args=[user.id])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.following.filter(id=user.id).exists())
        self.assertEqual(user.followers.count(), 1)
        self.assertEqual(
            response.data["message"], f"You followed user - {user.username}"
        )

    def test_list_user_followers(self):
        user1 = sample_user("test_user_1")
        user2 = sample_user("test_user_2")

        user1.following.add(self.user)
        user2.following.add(self.user)

        url = reverse("user:followers")

        response = self.client.get(url)

        users = get_user_model().objects.filter(following=self.user)
        serializer = UserSerializer(users, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_user_following(self):
        user1 = sample_user("test_user_1")
        user2 = sample_user("test_user_2")

        self.user.following.add(user1)
        self.user.following.add(user2)

        url = reverse("user:following")

        response = self.client.get(url)

        users = self.user.following.all()
        serializer = UserSerializer(users, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
