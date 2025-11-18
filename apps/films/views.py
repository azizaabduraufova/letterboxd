from django.shortcuts import render, get_object_or_404
import requests
from django.contrib.auth.decorators import login_required
from .tmdb_client import get_popular_films


def home_guest(request):
    return render(request, "films/home_guest.html")


@login_required
def home_authenticated(request):
    popular_films = get_popular_films()

    # For now: Fake friends activity
    friends_films = [
        {"title": "The Social Network", "poster_url": "https://m.media-amazon.com/images/M/MV5BMjlkNTE5ZTUtNGEwNy00MGVhLThmZjMtZjU1NDE5Zjk1NDZkXkEyXkFqcGc@._V1_.jpg", "friend_username": "alex"},
        {"title": "Interstellar", "poster_url": "https://m.media-amazon.com/images/I/91obuWzA3XL._AC_UF894,1000_QL80_.jpg", "friend_username": "mila"},
    ]

    return render(request, "films/home.html", {
        "popular_films": popular_films,
        "friends_films": friends_films,
    })

def films(request):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"

    response = requests.get(url)
    data = response.json()

    films = []
    if 'results' in data:
        for item in data['results']:
            films.append({
                'title': item['title'],
                'poster_path': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item['poster_path'] else None,
                'overview': item['overview'],
                'release_date': item['release_date']
            })

    context = {
        'films': films
    }
    return render(request, 'films/films.html', context)

def film_detail(request, slug):
    from .models import Film
    film = get_object_or_404(Film, slug=slug)
    reviews = film.reviews.order_by('-created_at')
    film.backdrop_url = f"https://image.tmdb.org/t/p/original{film.backdrop_path}"
    is_in_watchlist = request.user.is_authenticated and request.user.profile.watchlist.filter(id=film.id).exists()
    rating_range = range(1, 6)
    # latest reviews first
    context = {
        'film': film,
        'reviews': reviews,
        'is_in_watchlist': is_in_watchlist,
        'rating_range': rating_range,
    }
    return render(request, 'films/film_detail.html', context)

def actor_detail(request, slug):
    from .models import Actor
    actor = get_object_or_404(Actor, slug=slug)
    films = actor.films.all()
    return render(request, "films/actor_detail.html", {"actor": actor, "films": films})

def director_detail(request, slug):
    from .models import Director
    director = get_object_or_404(Director, slug=slug)
    films = director.films.all()
    return render(request, "films/director_detail.html", {"director": director, "films": films})