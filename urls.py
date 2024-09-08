from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', views.PostRetrieveUpdateDestroyView.as_view(), name='post-detail'),
    path('posts/<int:pk>/comments/', views.PostCommentsView.as_view(), name='post-comments'),
    path('posts/<int:post_pk>/comments/create/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', views.CommentRetrieveUpdateDestroyView.as_view(), name='comment-detail'),
    path('comments/<int:pk>/reply/', views.CommentReplyView.as_view(), name='comment-reply'),
    path('posts/<int:post_pk>/reactions/', views.PostReactionsView.as_view(), name='post-reactions'),
    path('comments/<int:comment_pk>/reactions/', views.CommentReactionsView.as_view(), name='comment-reactions'),
    path('reactions/<int:pk>/', views.ReactionRetrieveUpdateDestroyView.as_view(), name='reaction-detail'),
]