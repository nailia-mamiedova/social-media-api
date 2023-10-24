from django.urls import path, include
from rest_framework import routers

from user.views import CreateUserView, ManageUserView, UserViewSet

route = routers.DefaultRouter()
route.register("users", UserViewSet)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("", include(route.urls)),
]

app_name = "user"
