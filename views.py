import json
from django.forms import ValidationError
from django.http import HttpResponse
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Reaction
from .serializers import PostSummarySerializer, PostDetailSerializer, CommentSerializer, ReactionSerializer
from .pagination import PostPagination

class CustomJsonResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        kwargs['content_type'] = 'application/json; charset=utf-8'
        super().__init__(content=json.dumps(data, ensure_ascii=False), **kwargs)


class PostListCreateView(generics.ListCreateAPIView):
    pagination_class = PostPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        author_id = self.kwargs.get('author_id', None)

        queryset = Post.objects.annotate(
            comment_count=Count('comments', distinct=True),
            like_count=Count('reactions', filter=Q(reactions__reaction_type=Reaction.ReactionType.LIKE)),
            dislike_count=Count('reactions', filter=Q(reactions__reaction_type=Reaction.ReactionType.DISLIKE))
        ).select_related('author').order_by('-updated_at')

        if author_id == 'me':
            return queryset.filter(author=self.request.user)
        elif author_id:
            return queryset.filter(author_id=author_id)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostDetailSerializer
        return PostSummarySerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return CustomJsonResponse(response.data)


class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PostDetailSerializer

    def get_queryset(self):
        return Post.objects.annotate(
            like_count=Count('reactions', filter=Q(reactions__reaction_type=Reaction.ReactionType.LIKE)),
            dislike_count=Count('reactions', filter=Q(reactions__reaction_type=Reaction.ReactionType.DISLIKE))
        ).select_related('author')

    def perform_update(self, serializer):
        if self.get_object().author != self.request.user:
            raise PermissionDenied("You do not have permission to edit this post.")
        
        serializer.save(author=self.request.user)
        
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return CustomJsonResponse(response.data)
        

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs.get('post_pk', None)
        return Comment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_pk'))
        serializer.save(author=self.request.user, post=post)
        
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return CustomJsonResponse(response.data)

class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.get_object().author != self.request.user:
            raise PermissionDenied("You do not have permission to edit this comment.")
        
        serializer.save()
        
    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("You do not have permission to delete this comment.")
        
        instance.delete()
        
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return CustomJsonResponse(response.data)


class PostReactionsView(generics.ListCreateAPIView):
    serializer_class = ReactionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Reaction.objects.filter(post_id=self.kwargs['post_pk'])

    def perform_create(self, serializer):
        try:
            post = Post.objects.get(pk=self.kwargs['post_pk'])
        except Post.DoesNotExist:
            raise ValidationError("Post does not exist.")
        
        serializer.save(author=self.request.user, post=post)

class CommentReactionsView(generics.ListCreateAPIView):
    serializer_class = ReactionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Reaction.objects.filter(comment_id=self.kwargs['comment_pk'])

    def perform_create(self, serializer):
        try:
            comment = Comment.objects.get(pk=self.kwargs['comment_pk'])
        except Comment.DoesNotExist:
            raise ValidationError("Comment does not exist.")
        
        serializer.save(author=self.request.user, comment=comment)

class ReactionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        reaction = self.get_object()
        if reaction.author != self.request.user:
            raise PermissionDenied("You can only update your own reactions.")
        
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("You can only delete your own reactions.")
        
        instance.delete()