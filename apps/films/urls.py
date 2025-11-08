from django.urls import path
from django.shortcuts import render
from apps.films import views

urlpatterns = [
    path('', views.home, name='home'),
    path('films/', views.films, name='films'),
]
