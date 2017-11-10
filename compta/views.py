from django.shortcuts import render
from django.http import HttpResponse, Http404
from compta.models import Transaction, Compte, Budget

def hello(request):
    return HttpResponse("<h2>HEY! you</h2>")

def index(request):
    return render(request, 'compta/home.html')

def detail_compte(request, pk):
    try:
        compte = Compte.objects.get(pk=pk)
        transac = Transaction.objects.get(compte=pk)
    except:
        raise Http404("Le compte spécifié n'existe pas!")
    return render(request, "compta/detail_compte.html", {'compte': compte, 'transac':transac})

def detail_budget(request, pk):
    try:
        budget = Budget.objects.get(pk=pk)
        transac = Transaction.objects.get(compte=pk)
    except:
        raise Http404("Le Budget spécifié n'existe pas!")
    return render(request, "compta/detail_budget.html", {'budget': budget, 'transac':transac})