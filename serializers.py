from rest_framework import serializers
from .models import Post, Comment, Reaction
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class PostSummarySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'author', 'created_at', 'upvotes', 'downvotes', 'comment_count']

class PostDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at', 'upvotes', 'downvotes']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'post', 'parent', 'created_at', 'updated_at', 'upvotes', 'downvotes', 'replies']
        read_only_fields = ['post', 'parent']

    def get_replies(self, obj):
        if obj.is_max_depth():
            return []
        return CommentSerializer(obj.replies.all(), many=True).data

class ReactionSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'reaction_type', 'author', 'post', 'comment', 'created_at']
        read_only_fields = ['author', 'post', 'comment', 'created_at']