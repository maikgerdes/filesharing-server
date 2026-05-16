from django.http import HttpResponse
from django.shortcuts import render 
def movies(request):
    return render(request, 'movies/movies.html', {'movies': ['movie1, movie2']})

def home(request):
    return HttpResponse("Standard")