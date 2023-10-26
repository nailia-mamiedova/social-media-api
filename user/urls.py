from django.urls import path, include
from rest_framework import routers

from user.views import (
    CreateUserView,
    ManageUserView,
    UserViewSet,
    LoginUserView,
    LogoutUserView,
    AddFollower,
    RemoveFollower,
    MyFollowersList,
    MyFollowingList,
)

route = routers.DefaultRouter()
route.register("users", UserViewSet)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("login/", LoginUserView.as_view(), name="login"),
    path("logout/", LogoutUserView.as_view(), name="logout"),
    path("follow/<int:pk>/", AddFollower.as_view(), name="follow"),
    path("unfollow/<int:pk>/", RemoveFollower.as_view(), name="unfollow"),
    path("followers/", MyFollowersList.as_view(), name="followers"),
    path("following/", MyFollowingList.as_view(), name="following"),
    path("", include(route.urls)),
]

app_name = "user"
