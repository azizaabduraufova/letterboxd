from letterboxd import views
from django.urls import path

urlpatterns = [
    path('', views.genre_list_or_create),
    path('movies/', views.movie_list_or_create),
    path('<int:pk>/', views.genre_retrieve_update_or_delete),
    path('movies/<int:pk>/', views.movie_retrieve_update_or_delete),
    path('users/', views.user_list_or_create),
    path('users/<int:pk>/', views.user_retrieve_update_or_delete),
]