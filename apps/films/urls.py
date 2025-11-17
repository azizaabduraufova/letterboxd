from django.urls import path
from django.shortcuts import render
from apps.films import views

urlpatterns = [
    path('', views.home_guest, name='home_guest'),
    path('home/', views.home_authenticated, name='home_authenticated'),
    path('films/', views.films, name='films'),
]
