from django.urls import path, include
from rest_framework import routers

from post.views import PostViewSet, TagViewSet, LikeUnlikePost, CommentPost

route = routers.DefaultRouter()
route.register("posts", PostViewSet)
route.register("tags", TagViewSet)

urlpatterns = [
    path("", include(route.urls)),
    path("posts/<int:pk>/like/", LikeUnlikePost.as_view(), name="like-unlike"),
    path("posts/<int:pk>/comment/", CommentPost.as_view(), name="comment"),
]

app_name = "post"
