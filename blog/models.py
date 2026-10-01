from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    mood = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True)
    audio_file = models.FileField(upload_to='audio/', null=True, blank=True)
    spotify_link = models.URLField(null=True, blank=True)
    reading_time = models.IntegerField(default=1)
    
    # Reaction fields (calculated, not stored)
    # thumbs_up = models.IntegerField(default=0)
    # thumbs_down = models.IntegerField(default=0)
    # heart = models.IntegerField(default=0)
    
    # Saved blogs relationship
    saved_by = models.ManyToManyField(User, related_name='saved_blogs', blank=True)
    
    # NEW: Draft field
    is_draft = models.BooleanField(default=False)
    last_saved = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class Reaction(models.Model):
    REACTION_TYPES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('heart', 'Heart'),
    ]
    
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE, related_name='reactions')  # Fixed
    type = models.CharField(max_length=10, choices=REACTION_TYPES)
    session_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['blog', 'session_key', 'type']  # One reaction per session per blog


class Comment(models.Model):
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE, related_name='comments')  # Fixed
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Comment on {self.blog.title} by {self.author or "Anonymous"}'