from django.urls import path
from apps.profiles import views

urlpatterns = [
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('create-profile/', views.create_profile, name='create_profile'),
    path('sign-in/', views.sign_in, name='sign_in'),
]