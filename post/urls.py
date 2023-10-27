from django.urls import path, include
from rest_framework import routers

from post.views import PostViewSet, TagViewSet

route = routers.DefaultRouter()
route.register("posts", PostViewSet)
route.register("tags", TagViewSet)

urlpatterns = [path("", include(route.urls))]

app_name = "post"
