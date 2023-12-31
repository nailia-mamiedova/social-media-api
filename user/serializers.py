from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "bio",
            "picture",
            "password",
            "is_staff",
        )
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserCreateSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = (
            "email",
            "username",
            "password",
        )

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class UserListSerializer(UserSerializer):
    follow = serializers.SerializerMethodField()
    follow_unfollow = serializers.HyperlinkedIdentityField(
        view_name="user:follow-unfollow",
    )

    def get_follow(self, obj):
        request = self.context.get("request")
        if request:
            return request.user in obj.followers.all()
        return False

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "follow",
            "follow_unfollow",
        )


class UserDetailSerializer(UserListSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "bio",
            "picture",
            "is_staff",
            "follow",
            "follow_unfollow",
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
