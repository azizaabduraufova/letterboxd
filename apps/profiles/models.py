from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Favorites
    favorite_films = models.ManyToManyField('films.Film', related_name='favorited_by', blank=True)
    watchlist = models.ManyToManyField('films.Film', related_name='watchlisted_by', blank=True)

    # Following/followers
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def friends(self):
        """Mutual following"""
        return self.following.filter(followers=self)

    def save(self, *args, **kwargs):
        """Ensure no more than 4 favorite films"""
        super().save(*args, **kwargs)
        if self.favorite_films.count() > 4:
            raise ValueError("Cannot have more than 4 favorite films")

    def __str__(self):
        return self.user.username


class ProfileFilm(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    film = models.ForeignKey('films.Film', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('profile', 'film')

    def __str__(self):
        return f"{self.profile.user.username} - {self.film.title}"
