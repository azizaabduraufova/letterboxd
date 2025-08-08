from django.contrib import admin
from letterboxd.models import Genre, Movie, Profile

admin.site.register([Genre, Movie, Profile])