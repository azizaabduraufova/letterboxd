from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Movie(TimeStampModel):
    title = models.CharField(max_length=250)
    year = models.IntegerField()
    director = models.CharField(max_length=250)
    genres = models.ManyToManyField(Genre, related_name='movies')
    description = models.TextField(max_length=1000, blank=True, null=True)
    poster = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f'{self.title} ({self.year})'

    class Meta:
        unique_together = ('title', 'director')
        ordering = ['-year']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    img = models.ImageField(null=True, blank=True, upload_to='media/profile_pics')

    def __str__(self):
        return f"{self.user.username}'s Profile"