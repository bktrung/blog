from django.db import models
from django.contrib.auth.models import User

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Post(TimeStampedModel):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')


class Comment(TimeStampedModel):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    

class Reaction(TimeStampedModel):
    class ReactionType(models.IntegerChoices):
        LIKE = 1, 'Like'
        DISLIKE = -1, 'Dislike'

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reactions', null=True, blank=True)
    reaction_type = models.SmallIntegerField(choices=ReactionType.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'post'],
                condition=models.Q(post__isnull=False),
                name='unique_post_reaction'
            ),
            models.UniqueConstraint(
                fields=['author', 'comment'],
                condition=models.Q(comment__isnull=False),
                name='unique_comment_reaction'
            ),
        ]