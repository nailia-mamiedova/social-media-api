from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.hashers import check_password
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework import generics, mixins, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView

from user.models import User
from user.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
)


@extend_schema_view(
    list=extend_schema(description="Display all users"),
    retrieve=extend_schema(description="Display user with specified id"),
)
class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = self.queryset

        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset.exclude(pk=self.request.user.pk)

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer

        if self.action == "retrieve":
            return UserDetailSerializer

        return UserSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="username",
                description="Filter users by username",
                type=OpenApiTypes.STR,
                required=False,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(
    description="Register with email, username and password",
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer


@extend_schema_view(
    list=extend_schema(description="Display user profile"),
    update=extend_schema(description="Update user profile"),
    partial_update=extend_schema(description="Update user profile"),
    delete=extend_schema(description="Delete user profile"),
)
class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class LoginUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = {}
        req_body = json.loads(request.body)
        email = req_body["email"]
        password = req_body["password"]
        try:
            account = get_user_model().objects.get(email=email)
        except BaseException:
            raise ValidationError({"400": f"There is no user with email - {email}"})

        token = Token.objects.get_or_create(user=account)[0].key
        if not check_password(password, account.password):
            raise ValidationError({"message": "Incorrect Login credentials"})

        if account:
            if account.is_active:
                login(request, account)
                data["message"] = "User Logged in successfully"
                data["email_address"] = account.email

                res = {"data": data, "token": token}

                return Response(res)

            else:
                raise ValidationError({"400": f"Account not active"})

        else:
            raise ValidationError({"400": f"Account doesnt exist"})


class LogoutUserView(APIView):
    @extend_schema(
        description="Logout and delete user token",
        responses=OpenApiTypes.STR,
    )
    def get(self, request):
        request.user.auth_token.delete()
        logout(request)

        return Response("User Logged out successfully")


class FollowUnfollow(APIView):
    @extend_schema(
        description="Follow or unfollow(if already followed) user with specified id",
        responses=OpenApiTypes.STR,
    )
    def post(self, request, pk, *args, **kwargs):
        profile = User.objects.get(pk=pk)

        if request.user in profile.followers.all():
            profile.followers.remove(request.user)
            return Response("You unfollowed user - " + profile.username)

        profile.followers.add(request.user)
        return Response("You followed user - " + profile.username)


@extend_schema(description="Display all user followers")
class MyFollowersList(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.followers.all()


@extend_schema(description="Display all user following")
class MyFollowingList(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.following.all()
