from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True, max_length=5000)
    genres = models.ManyToManyField(Genre, related_name='actors', blank=True)
    films = models.ManyToManyField('Film', related_name='acted_in', blank=True)

    def __str__(self):
        return self.name


class Director(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True, max_length=5000)
    genres = models.ManyToManyField(Genre, related_name='directors', blank=True)
    films = models.ManyToManyField('Film', related_name='directed_by', blank=True)

    def __str__(self):
        return self.name


class Film(models.Model):
    title = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    directors = models.ManyToManyField(Director, related_name='films_directed', blank=True)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    poster = models.URLField(blank=True, null=True, max_length=5000)
    actors = models.ManyToManyField(Actor, related_name='actors', blank=True)
    genres = models.ManyToManyField(Genre, related_name='films', blank=True)
    duration = models.PositiveIntegerField(help_text='Duration in minutes', blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    rating = models.DecimalField(decimal_places=1, max_digits=2, blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.year})"


class Review(models.Model):
    profile = models.ForeignKey('profiles.Profile', on_delete=models.CASCADE, related_name='reviews')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'film')

    def __str__(self):
        return f"{self.profile.user.username} - {self.film.title}: {self.rating}/10"
