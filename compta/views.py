from django.shortcuts import render
from django.http import HttpResponse

def hello(request):
    return HttpResponse("<h2>HEY! you</h2>")

def index(request):
    return render(request, 'compta/home.html')

