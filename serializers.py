from rest_framework import serializers
from .models import Post, Comment, Reaction
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class PostSummarySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comment_count = serializers.IntegerField(default=0)
    like_count = serializers.IntegerField(default=0)
    dislike_count = serializers.IntegerField(default=0)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'author', 'created_at', 'like_count', 'dislike_count', 'comment_count']


class PostDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(default=0)
    dislike_count = serializers.IntegerField(default=0)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at', 'like_count', 'dislike_count']
        

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'post', 'created_at', 'updated_at', 'like_count', 'dislike_count']
        read_only_fields = ['post', 'created_at']


class ReactionSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'reaction_type', 'author', 'post', 'comment', 'created_at']
        read_only_fields = ['post', 'comment', 'created_at']