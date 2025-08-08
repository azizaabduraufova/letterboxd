from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from letterboxd.models import Genre, Movie, Profile
from letterboxd.serializers import GenreSerializer, MovieSerializer, UserProfileSerializer
from django.db.models import Q

# CRUD for Genre
@api_view(['GET', 'POST'])
def genre_list_or_create(request, format=None):
    if request.method == 'GET':
        genres = Genre.objects.all()
        search = request.query_params.get('search', None)
        if search:
            genres = genres.filter(name__icontains=search)
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = GenreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def genre_retrieve_update_or_delete(request, pk, format=None):
    try:
        genre = Genre.objects.get(pk=pk)
    except Genre.DoesNotExist:
        return Response({"message": "Object not found"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = GenreSerializer(genre)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        serializer = GenreSerializer(genre, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        genre.delete()
        return Response({"message": "Object is deleted!"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def movie_list_or_create(request, format=None):
    if request.method == 'GET':
        title = request.query_params.get('title')
        year  = request.query_params.get('year')
        director = request.query_params.get('director')
        genre = request.query_params.get('genre')
        filters = Q()
        if title:
            filters &= Q(title__icontains=title)
        if year:
            filters &= Q(year=year)
        if director:
            filters &= Q(director__icontains=director)
        if genre:
            filters &= Q(genres__name__icontains=genre)
        movies = Movie.objects.filter(filters).distinct()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def movie_retrieve_update_or_delete(request, pk, format=None):
    try:
        movie = Movie.objects.get(pk=pk)
    except Movie.DoesNotExist:
        return Response({"message": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MovieSerializer(movie)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = MovieSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        movie.delete()
        return Response({"message": "Object is deleted!"}, status=status.HTTP_204_NO_CONTENT)