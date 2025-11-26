import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from apps.films.models import Review
from .forms import CustomUserCreationForm, SignInForm, UserProfileForm, ReviewForm
from .models import Profile, ProfileFilm, WatchedFilm


# def profile(request, username):
#     user = get_object_or_404(User, username=username)
#     context = {
#         'profile_user': user,
#     }
#     return render(request, 'profiles/profile.html', context)


def create_profile(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            messages.success(request, "Account created successfully!")
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'profiles/create_profile.html', {'form': form})


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
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")

    return render(request, "profiles/sign_in.html", {"form": form})


def profile_view(request, username):
    from apps.films.models import Film
    # Get the Profile object for the user being viewed
    user_profile = get_object_or_404(Profile, user__username=username)

    # Check if the logged-in user (request.user) is viewing their own profile
    is_own_profile = user_profile.user == request.user

    # Check if the logged-in user is following the user being viewed
    is_following = False
    if request.user.is_authenticated and not is_own_profile:
        is_following = user_profile.followers.filter(user=request.user).exists()

    # Favorite films (max 4)
    favorite_films = user_profile.favorite_films.all()[:4]

    # Total films watched (assuming you track it via reviews or watchlist)
    total_films = user_profile.watched_films.count()

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
        'is_own_profile': is_own_profile,  # Distinguish between own vs other profile
        'is_following': is_following,  # Whether logged-in user is following this profile
    }

    return render(request, 'profiles/profile.html', context)


def profile_films(request, username):
    user_profile = get_object_or_404(Profile, user__username=username)
    films = user_profile.watched_films.all()  # or watchlist if that's what you want
    return render(request, "profiles/profile_films.html", {
        "films": films
    })


def profile_stats(request, username):
    user_profile = get_object_or_404(Profile, user__username=username)

    # Followers and following
    following_profiles = user_profile.following.all()
    follower_profiles = user_profile.followers.all()

    # Extract profiles into a list of dictionaries
    following_users = [
        {
            'username': p.user.username,
            'avatar_url': p.avatar.url if p.avatar else None,
            'followers_count': p.followers.count(),
            'following_count': p.following.count(),
            'watched_films': WatchedFilm.objects.filter(profile=p).select_related('film')[:6]
        }
        for p in following_profiles
    ]

    follower_users = [
        {
            'username': p.user.username,
            'avatar_url': p.avatar.url if p.avatar else None,
            'followers_count': p.followers.count(),
            'following_count': p.following.count(),
            'watched_films': WatchedFilm.objects.filter(profile=p).select_related('film')[:6]
        }
        for p in follower_profiles
    ]

    return render(request, "profiles/profile_stats.html", {
        "profile_user": user_profile.user,
        "following_users": following_users,
        "follower_users": follower_users,
    })


@login_required
def edit_profile(request, username):
    user_profile = get_object_or_404(Profile, user__username=username)

    if request.user != user_profile.user:
        return HttpResponseForbidden("You don't have permission to edit this profile.")

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=user_profile.user.username)
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'profiles/edit_profile.html', {
        'form': form,
        'user_profile': user_profile,
    })


@login_required
def toggle_follow(request, username):
    target_profile = get_object_or_404(Profile, user__username=username)
    user_profile = request.user.profile

    # prevent following yourself
    if target_profile == user_profile:
        return redirect(reverse('profile', args=[username]))

    # follow/unfollow logic
    if target_profile in user_profile.following.all():
        user_profile.following.remove(target_profile)
    else:
        user_profile.following.add(target_profile)

    return redirect(reverse('profile', args=[username]))


@login_required
def logout_view(request):
    if request.method == "POST":
        # Logs out the user
        logout(request)
        return redirect("home_guest")  # Redirect to confirmation page
    return render(request, "profiles/logout_confirm.html")


def review_detail(request, username, review_id):
    # Fetch the Profile using the username
    profile_user = get_object_or_404(Profile, user__username=username)

    # Fetch the Review and ensure it belongs to the correct Profile
    review = get_object_or_404(Review, id=review_id, profile=profile_user)

    # Pass both the review and profile_user to the template
    return render(request, 'profiles/review_detail.html', {
        'review': review,
        'profile_user': profile_user,
    })


@login_required
def edit_review(request, username, review_id):
    # Fetch the Profile using the username
    profile_user = get_object_or_404(Profile, user__username=username)

    # Ensure the user can only edit their own reviews
    if request.user != profile_user.user:
        messages.error(request, "You don't have permission to edit this review.")
        return redirect('review_detail', username=username, review_id=review_id)

    # Fetch the Review object
    review = get_object_or_404(Review, id=review_id, profile=profile_user)

    # Handle the form submission
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            # messages.success(request, "Your review has been updated.")
            return redirect('review_detail', username=username, review_id=review.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'profiles/edit_review.html', {
        'form': form,
        'review': review,
        'profile_user': profile_user,
    })


@login_required
def delete_review(request, username, review_id):
    profile_user = get_object_or_404(Profile, user__username=username)
    review = get_object_or_404(Review, id=review_id, profile=profile_user)

    # Debugging Request Type
    print(f"Request Method: {request.method}")

    if request.method == "POST":
        print("Deleting review...")
        review.delete()
        # messages.success(request, "Your review has been deleted.")
        return redirect('profile', username=request.user.username)

    # For a GET request, render the confirmation page
    print("Rendering confirmation page...")
    return render(request, 'profiles/delete_review.html', {
        'review': review,
        'profile_user': profile_user,
    })