# apps/films/management/commands/import_tmdb.py
import os

from django.core.management.base import BaseCommand
from apps.films.models import Film, Actor, Director, Genre
from tmdbv3api import TMDb, Movie, Person

tmdb = TMDb()
tmdb.api_key = os.getenv("TMDB_API_KEY")
tmdb.language = "en"

movie_api = Movie()
person_api = Person()

class Command(BaseCommand):
    help = "Import ~100 films from 2000s and 2010s from TMDb, including actors and directors"

    def handle(self, *args, **kwargs):
        for decade_start in [2000, 2010]:
            films_added = 0
            page = 1
            self.stdout.write(f"Importing films from {decade_start}s...")

            while films_added < 100:
                popular_movies = movie_api.popular(page=page)

                if not popular_movies:
                    break

                # Filter by decade
                decade_movies = [m for m in popular_movies
                                 if m.release_date and decade_start <= int(m.release_date[:4]) <= decade_start+9]

                for m in decade_movies:
                    if films_added >= 100:
                        break

                    # Convert rating 0-10 → 0-5
                    rating_5 = round(m.vote_average / 2, 1) if m.vote_average else None

                    film, created = Film.objects.get_or_create(
                        title=m.title,
                        year=int(m.release_date.split('-')[0]) if m.release_date else 0,
                        defaults={
                            'poster': f"https://image.tmdb.org/t/p/w500{m.poster_path}" if m.poster_path else None,
                            'description': m.overview,
                            'rating': rating_5,
                            'duration': m.runtime if hasattr(m, 'runtime') else None
                        }
                    )

                    # Genres
                    if hasattr(m, 'genres') and m.genres:
                        for g in m.genres:
                            genre, _ = Genre.objects.get_or_create(name=g['name'])
                            film.genres.add(genre)

                    # Credits
                    credits = movie_api.credits(m.id)

                    crew_list = list(getattr(credits, 'crew', []))
                    for crew_member in crew_list:
                        if crew_member.job == 'Director':
                            person_detail = person_api.details(crew_member.id)
                            director, _ = Director.objects.get_or_create(
                                name=crew_member.name,
                                defaults={
                                    'bio': getattr(person_detail, 'biography', ''),
                                    'image': f"https://image.tmdb.org/t/p/w500{person_detail.profile_path}"
                                    if getattr(person_detail, 'profile_path', None) else None
                                }
                            )
                            film.directors.add(director)

                        # Top 5 actors safely
                        cast_list = list(getattr(credits, 'cast', []))  # convert to normal list
                        for cast_member in cast_list[:5]:
                            person_detail = person_api.details(cast_member.id)
                            actor, _ = Actor.objects.get_or_create(
                                name=cast_member.name,
                                defaults={
                                    'bio': getattr(person_detail, 'biography', ''),
                                    'image': f"https://image.tmdb.org/t/p/w500{person_detail.profile_path}"
                                    if getattr(person_detail, 'profile_path', None) else None
                                }
                            )
                            film.actors.add(actor)


                    film.save()
                    films_added += 1
                    self.stdout.write(self.style.SUCCESS(f"Added {film.title} ({film.year})"))

                page += 1

            self.stdout.write(self.style.SUCCESS(f"Finished importing {films_added} films from {decade_start}s."))

        self.stdout.write(self.style.SUCCESS("All done!"))
