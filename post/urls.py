from django.urls import path, include
from rest_framework import routers

from post.views import PostViewSet, TagViewSet

route = routers.DefaultRouter()
route.register("post", PostViewSet, basename="post")
route.register("tag", TagViewSet)

urlpatterns = [path("", include(route.urls))]

app_name = "post"
