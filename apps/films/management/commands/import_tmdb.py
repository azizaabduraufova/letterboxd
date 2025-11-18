# apps/films/management/commands/import_tmdb.py
import os
from tmdbv3api import TMDb, Movie, Person
from django.core.management.base import BaseCommand
from apps.films.models import Film, Actor, Director, Genre

tmdb = TMDb()
tmdb.api_key = os.getenv("TMDB_API_KEY")
tmdb.language = "en"

movie_api = Movie()
person_api = Person()

class Command(BaseCommand):
    help = "Import 100 films per decade from TMDb with full details and proper connections"

    def handle(self, *args, **kwargs):
        # Delete old data
        self.stdout.write("Deleting existing films, actors, directors, and genres...")
        Film.objects.all().delete()
        Actor.objects.all().delete()
        Director.objects.all().delete()
        Genre.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Deleted all existing records."))

        decades = [
            (2000, 2009, 100),
            (2010, 2019, 100),
            (2020, 2025, 100)
        ]

        for start_year, end_year, limit in decades:
            films_added = 0
            page = 1
            self.stdout.write(f"Importing films from {start_year}-{end_year}...")

            while films_added < limit:
                popular_movies = movie_api.popular(page=page)
                if not popular_movies:
                    break

                for m in popular_movies:
                    movie_detail = movie_api.details(m.id)
                    if not movie_detail.release_date:
                        continue
                    year = int(movie_detail.release_date[:4])
                    if year < start_year or year > end_year:
                        continue
                    if films_added >= limit:
                        break

                    # Rating 0-10 → 0-5
                    rating_5 = round(movie_detail.vote_average / 2, 1) if movie_detail.vote_average else None

                    LANGUAGE_CODES = {
                        'en': 'English',
                        'fr': 'French',
                        'es': 'Spanish',
                        'de': 'German',
                        'it': 'Italian',
                        'ja': 'Japanese',
                        'zh': 'Chinese',
                        'ko': 'Korean',
                        'hi': 'Hindi',
                        # ... add more as needed
                    }

                    lang_code = movie_detail.original_language
                    language_name = LANGUAGE_CODES.get(lang_code, lang_code)

                    # Create Film
                    film, created = Film.objects.get_or_create(
                        title=movie_detail.title,
                        year=year,
                        defaults={
                            'poster': f"https://image.tmdb.org/t/p/w500{movie_detail.poster_path}" if movie_detail.poster_path else None,
                            'backdrop_path' : f"https://image.tmdb.org/t/p/original{movie_detail.backdrop_path}" if movie_detail.backdrop_path else None,
                            'description': movie_detail.overview,
                            'rating': rating_5,
                            'duration': movie_detail.runtime,
                            'tagline': movie_detail.tagline,
                            'language': language_name,
                            'country': movie_detail.production_countries[0]['name'] if movie_detail.production_countries else None
                        }
                    )
                    film.save()  # crucial before M2M

                    # Genres
                    film_genres = []
                    for g in getattr(movie_detail, 'genres', []):
                        genre, _ = Genre.objects.get_or_create(name=g['name'])
                        film.genres.add(genre)
                        film_genres.append(genre)

                    # Credits
                    credits = movie_api.credits(m.id)

                    # Directors
                    for crew_member in getattr(credits, 'crew', []):
                        if crew_member.job == 'Director':
                            person_detail = person_api.details(crew_member.id)
                            director, _ = Director.objects.get_or_create(
                                name=crew_member.name,
                                defaults={
                                    'bio': getattr(person_detail, 'biography', ''),
                                    'image': f"https://image.tmdb.org/t/p/w500{getattr(person_detail, 'profile_path', '')}" if getattr(person_detail, 'profile_path', None) else None
                                }
                            )
                            director.save()
                            film.directors.add(director)
                            for genre in film_genres:
                                director.genres.add(genre)

                    # Top 5 actors
                    for cast_member in list(getattr(credits, 'cast', []))[:5]:
                        person_detail = person_api.details(cast_member.id)
                        actor, _ = Actor.objects.get_or_create(
                            name=cast_member.name,
                            defaults={
                                'bio': getattr(person_detail, 'biography', ''),
                                'image': f"https://image.tmdb.org/t/p/w500{getattr(person_detail, 'profile_path', '')}" if getattr(person_detail, 'profile_path', None) else None
                            }
                        )
                        actor.save()
                        film.actors.add(actor)
                        for genre in film_genres:
                            actor.genres.add(genre)

                    films_added += 1
                    self.stdout.write(self.style.SUCCESS(f"Added {film.title} ({film.year})"))

                page += 1

            self.stdout.write(self.style.SUCCESS(f"Finished importing {films_added} films from {start_year}-{end_year}."))

        self.stdout.write(self.style.SUCCESS("All done!"))
