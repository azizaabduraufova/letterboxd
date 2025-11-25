from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True, max_length=5000)
    genres = models.ManyToManyField(Genre, related_name='actors', blank=True)
    # films = models.ManyToManyField('Film', related_name='acted_in', blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('actor_detail', args=[self.slug])

    def __str__(self):
        return self.name


class Director(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True, max_length=5000)
    genres = models.ManyToManyField(Genre, related_name='directors', blank=True)
    # films = models.ManyToManyField('Film', related_name='directed_by', blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('director_detail', args=[self.slug])

    def __str__(self):
        return self.name


class Film(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    year = models.PositiveIntegerField()
    directors = models.ManyToManyField(Director, related_name='films', blank=True)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    poster = models.URLField(blank=True, null=True, max_length=5000)
    backdrop_path = models.URLField(blank=True, null=True, max_length=5000)
    actors = models.ManyToManyField(Actor, related_name='films', blank=True)
    genres = models.ManyToManyField(Genre, related_name='films', blank=True)
    duration = models.PositiveIntegerField(help_text='Duration in minutes', blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    rating = models.DecimalField(decimal_places=1, max_digits=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.year}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('film_detail', args=[self.slug])

    def __str__(self):
        return f"{self.title} ({self.year})"


class Review(models.Model):
    profile = models.ForeignKey('profiles.Profile', on_delete=models.CASCADE, related_name='reviews')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='reviews')
    rating = models.DecimalField(decimal_places=1, max_digits=2, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'film')

    def __str__(self):
        return f"{self.profile.user.username} - {self.film.title}: {self.rating}/10"


