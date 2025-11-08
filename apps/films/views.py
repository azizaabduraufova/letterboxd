from django.shortcuts import render
import requests

TMDB_API_KEY = "cd8679f22c6bc5735a385891f4c6fa73"

def home(request):
    if request.user.is_authenticated:
        return render(request, 'films/home_guest.html')
    return render(request, 'films/home.html')

def films(request):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"

    response = requests.get(url)
    data = response.json()

    films = []
    if 'results' in data:
        for item in data['results']:
            films.append({
                'title': item['title'],
                'poster_path': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item['poster_path'] else None,
                'overview': item['overview'],
                'release_date': item['release_date']
            })

    context = {
        'films': films
    }
    return render(request, 'films/films.html', context)