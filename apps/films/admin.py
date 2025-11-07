from django.contrib import admin
from apps.films.models import Film, Actor, Director, Genre, Review

admin.site.register(Film)
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Genre)
admin.site.register(Review)