from django.urls import path
from .views import PostListAPIView, PostCreateView, PostRetrieveUpdateDestroyView, PostCommentListView, PostCommentCreateView, \
    CommentListCreateApiView, CommentLikeListView, PostLikeListView, CommentLikeCreateView, PostLikeView, CommentLikeView


urlpatterns = [
    path('list/', PostListAPIView.as_view()),
    path('create/', PostCreateView.as_view()),
    path('<uuid:pk>/', PostRetrieveUpdateDestroyView.as_view()),
    path('<uuid:pk>/likes/', PostLikeListView.as_view()),
    path('<uuid:pk>/comments/', PostCommentListView.as_view()),
    path('<uuid:pk>/comments/create/', PostCommentCreateView.as_view()),
    

    path('comment/', CommentListCreateApiView.as_view()),
    path('comment/<uuid:pk>/likes/', CommentLikeListView.as_view()),
    path('comment/like/create/', CommentLikeCreateView.as_view()),

    path("<uuid:pk>/create-delete-like/", PostLikeView.as_view()),
    path("comment/<uuid:pk>/create-delete-like/", CommentLikeView.as_view()),
]
