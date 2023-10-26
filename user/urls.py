from django.urls import path, include
from rest_framework import routers

from user.views import (
    CreateUserView,
    ManageUserView,
    UserViewSet,
    LoginUserView,
    LogoutUserView,
)

route = routers.DefaultRouter()
route.register("users", UserViewSet)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("login/", LoginUserView.as_view(), name="login"),
    path("logout/", LogoutUserView.as_view(), name="logout"),
    path("", include(route.urls)),
]

app_name = "user"
