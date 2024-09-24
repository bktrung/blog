from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<str:author_id>', views.PostListCreateView.as_view(), name='post-list-by-author'),
    path('posts/<int:pk>/', views.PostRetrieveUpdateDestroyView.as_view(), name='post-detail'),
    path('posts/<int:post_pk>/comments/', views.CommentListCreateView.as_view(), name='post-comments-list-create'),
    path('comments/<int:pk>/', views.CommentRetrieveUpdateDestroyView.as_view(), name='comment-update-delete'),
    path('posts/<int:post_pk>/reactions/', views.PostReactionsView.as_view(), name='post-reactions'),
    path('comments/<int:comment_pk>/reactions/', views.CommentReactionsView.as_view(), name='comment-reactions'),
    path('reactions/<int:pk>/', views.ReactionRetrieveUpdateDestroyView.as_view(), name='reaction-update-delete'),
]