import os

from tmdbv3api import TMDb, Movie

tmdb = TMDb()
tmdb.api_key = os.getenv("TMDB_API_KEY")
tmdb.language = "en"
tmdb.debug = True

movie_api = Movie()
# person_api = Person()

def get_popular_films():
    movies = list(movie_api.popular())  # TMDb popular movies
    results = []
    for m in movies[:6]:  # First 6
        results.append({
            "title": m.title,
            "poster_url": f"https://image.tmdb.org/t/p/w500{m.poster_path}" if m.poster_path else "",
        })
    return results
