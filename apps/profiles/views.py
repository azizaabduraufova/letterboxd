import os

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .forms import SignInForm
from django.shortcuts import render, get_object_or_404
from .models import  Profile, ProfileFilm, WatchedFilm
from django.contrib.auth import authenticate, login, logout


def profile(request, username):
    user = get_object_or_404(User, username=username)
    context = {
        'profile_user': user,
    }
    return render(request, 'profiles/profile.html', context)

def create_profile(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            messages.success(request, "Account created successfully!")
            return redirect('home_authenticated')
    else:
        form = CustomUserCreationForm()

    return render(request, 'profiles/create_profile.html', {'form': form})

@csrf_exempt
def sign_in(request):
    form = SignInForm()

    if request.method == "POST":
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect("home_authenticated")
            else:
                messages.error(request, "Invalid username or password.")

    return render(request, "profiles/sign_in.html", {"form": form})


def profile_view(request, username):
    from apps.films.models import Film
    # Get the Profile object
    user_profile = get_object_or_404(Profile, user__username=username)

    # Favorite films (max 4)
    favorite_films = user_profile.favorite_films.all()[:4]

    # Total films watched (assuming you track it via reviews or watchlist)
    total_films = user_profile.watched_films.count()+favorite_films.count()

    # Followers / following counts
    following_count = user_profile.following.count()
    followers_count = user_profile.followers.count()

    # Recent films watched (e.g., last 4 reviews)
    watched_films = WatchedFilm.objects.filter(profile=user_profile) \
        .order_by('-watched_at')[:4] \
        .select_related('film')

    # Extract the Film objects
    last_watched = [wf.film for wf in watched_films]

    # Last 3 reviews
    recent_reviews = user_profile.reviews.order_by('-created_at')[:3]

    context = {
        'user_profile': user_profile,
        "watched_films": watched_films,
        'total_films': total_films,
        'following_count': following_count,
        'followers_count': followers_count,
        'favorite_films': favorite_films,
        'recent_films': last_watched,
        'recent_reviews': recent_reviews,
    }

    return render(request, 'profiles/profile.html', context)