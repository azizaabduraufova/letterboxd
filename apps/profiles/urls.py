from django.urls import path
from apps.profiles import views

urlpatterns = [
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('create-profile/', views.create_profile, name='create_profile'),
    path('sign-in/', views.sign_in, name='sign_in'),
    path('profile/<str:username>/films', views.profile_films, name='profile_films'),
    path('profile/<str:username>/stats', views.profile_stats, name='profile_stats'),
    path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/review/<int:review_id>/', views.review_detail, name='review_detail'),
    path('profile/<str:username>/review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('profile/<str:username>/review/<int:review_id>/delete/', views.delete_review, name='delete_review'),

]
