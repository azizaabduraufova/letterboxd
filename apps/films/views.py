import os

from django.shortcuts import render, get_object_or_404, redirect
import requests
from django.contrib.auth.decorators import login_required
from .tmdb_client import get_popular_films
from apps.films.models import Film, Actor, Director, Review
from apps.profiles.models import WatchedFilm
from .forms import ReviewForm
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
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"

    response = requests.get(url)
    data = response.json()

    films_list = []
    if 'results' in data:
        for item in data['results']:
            # Create or update film in DB
            film, created = Film.objects.get_or_create(
                title=item['title'],
                defaults={
                    'poster': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get('poster_path') else None,
                    'backdrop_path': f"https://image.tmdb.org/t/p/original{item['backdrop_path']}" if item.get('backdrop_path') else None,
                    'year': int(item['release_date'].split('-')[0]) if item.get('release_date') else None,
                }
            )
            films_list.append(film)

    context = {
        'films': films_list
    }
    return render(request, 'films/films.html', context)

def film_detail(request, slug):
    film = get_object_or_404(Film, slug=slug)
    reviews = film.reviews.order_by('-created_at')
    film.backdrop_url = f"https://image.tmdb.org/t/p/original{film.backdrop_path}"
    is_in_watchlist = request.user.is_authenticated and request.user.profile.watchlist.filter(id=film.id).exists()
    rating_range = range(1, 6)
    watched = (
            request.user.is_authenticated
            and request.user.profile.watched_films.filter(id=film.id).exists()
    )

    # latest reviews first
    context = {
        'film': film,
        'reviews': reviews,
        'is_in_watchlist': is_in_watchlist,
        'rating_range': rating_range,
        'watched': watched,
    }
    return render(request, 'films/film_detail.html', context)

def actor_detail(request, slug):
    actor = get_object_or_404(Actor, slug=slug)
    films = actor.films.all()
    return render(request, "films/actor_detail.html", {"actor": actor, "films": films})

def director_detail(request, slug):
    director = get_object_or_404(Director, slug=slug)
    films = director.films.all()
    return render(request, "films/director_detail.html", {"director": director, "films": films})

@login_required
def mark_as_watched(request, slug):
    film = get_object_or_404(Film, slug=slug)
    profile = request.user.profile

    WatchedFilm.objects.get_or_create(profile=profile, film=film)
    return redirect('film_detail', slug=slug)

@login_required
def toggle_watchlist(request, slug):
    film = get_object_or_404(Film, slug=slug)
    profile = request.user.profile

    if film in profile.watchlist.all():
        profile.watchlist.remove(film)
    else:
        profile.watchlist.add(film)

    return redirect('film_detail', slug=slug)

@login_required
def review_film(request, slug):
    return redirect('create_review', slug=slug)

def film_reviews(request, slug):
    film = get_object_or_404(Film, slug=slug)
    reviews = film.reviews.select_related('profile__user').order_by('-created_at')
    film.backdrop_url = f"https://image.tmdb.org/t/p/original{film.backdrop_path}"

    context = {
        'film': film,
        'reviews': reviews,

    }
    return render(request, 'films/review_list.html', context)

@login_required
def create_view(request, slug):
    film = get_object_or_404(Film, slug=slug)
    film.backdrop_url = f"https://image.tmdb.org/t/p/original{film.backdrop_path}"

    # prevent duplicate reviews
    if Review.objects.filter(film=film, profile=request.user.profile).exists():
        return redirect('film_reviews', slug=slug)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.film = film
            review.profile = request.user.profile
            review.save()
            return redirect('film_reviews', slug=slug)
    else:
        form = ReviewForm()

    return render(request, 'films/review_film.html', {
        'film': film,
        'form': form
    })
