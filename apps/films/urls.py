from django.urls import path
from django.shortcuts import render
from apps.films import views

urlpatterns = [
    path('', views.home_guest, name='home_guest'),
    path('home/', views.home_authenticated, name='home_authenticated'),
    path('films/', views.films, name='films'),
    path('film/<slug:slug>/', views.film_detail, name='film_detail'),
    path('actor/<slug:slug>/', views.actor_detail, name='actor_detail'),
    path('director/<slug:slug>/', views.director_detail, name='director_detail'),
    path('film/<slug:slug>/watch/', views.mark_as_watched, name='mark_as_watched'),
    path('film/<slug:slug>/watchlist/toggle/', views.toggle_watchlist, name='toggle_watchlist'),
    path('film/<slug:slug>/review/', views.create_view, name='review_film'),
    path("film/<slug:slug>/reviews/", views.film_reviews, name="film_reviews"),

]
