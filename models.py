from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class VotableModel(models.Model):
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def update_vote_count(self, reaction_type, increment=True):
        if reaction_type == Reaction.ReactionType.UPVOTE:
            self.upvotes = models.F('upvotes') + (1 if increment else -1)
        elif reaction_type == Reaction.ReactionType.DOWNVOTE:
            self.downvotes = models.F('downvotes') + (1 if increment else -1)
        self.save(update_fields=['upvotes', 'downvotes'])

class Post(TimeStampedModel, VotableModel):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
        ]

    def __str__(self):
        return self.title

class Comment(TimeStampedModel, VotableModel):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    depth = models.PositiveIntegerField(default=0)
    max_depth = models.PositiveIntegerField(default=2)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'parent', 'created_at']),
        ]

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'
    
    def is_max_depth(self):
        return self.depth >= self.max_depth
    
    def clean(self):
        if self.parent and self.depth >= self.max_depth:
            raise ValidationError("Comment depth exceeds maximum allowed.")
        super().clean()

    def save(self, *args, **kwargs):
        if self.parent:
            self.depth = self.parent.depth + 1
        super().save(*args, **kwargs)

class Reaction(TimeStampedModel):
    class ReactionType(models.IntegerChoices):
        UPVOTE = 1, 'Upvote'
        DOWNVOTE = -1, 'Downvote'

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
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['comment']),
        ]

    def __str__(self):
        return f'Reaction by {self.author} on {"post" if self.post else "comment"}'
    
    def save(self, *args, **kwargs):
        created = not self.pk
        if not created:
            old_reaction = Reaction.objects.get(pk=self.pk)
            if old_reaction.reaction_type != self.reaction_type:
                if old_reaction.post:
                    old_reaction.post.update_vote_count(old_reaction.reaction_type, increment=False)
                elif old_reaction.comment:
                    old_reaction.comment.update_vote_count(old_reaction.reaction_type, increment=False)
        super().save(*args, **kwargs)
        if created:
            if self.post:
                self.post.update_vote_count(self.reaction_type, increment=True)
            elif self.comment:
                self.comment.update_vote_count(self.reaction_type, increment=True)

    def delete(self, *args, **kwargs):
        if self.post:
            self.post.update_vote_count(self.reaction_type, increment=False)
        elif self.comment:
            self.comment.update_vote_count(self.reaction_type, increment=False)
        super().delete(*args, **kwargs)