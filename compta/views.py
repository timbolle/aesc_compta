from django.shortcuts import render
from django.http import HttpResponse, Http404
from compta.models import Transaction, Compte, Budget
import csv
from datetime import datetime

def hello(request):
    return HttpResponse("<h2>HEY! you</h2>")

def index(request):
    return render(request, 'compta/home.html')

def detail_compte(request, pk):
    try:
        compte = Compte.objects.get(pk=pk)
        transac = Transaction.objects.filter(compte=pk)
    except:
        raise Http404("Le compte spécifié n'existe pas!")
    return render(request, "compta/detail_compte.html", {'compte': compte, 'transac':transac})

def detail_budget(request, pk):
    try:
        budget = Budget.objects.get(pk=pk)
        transac = Transaction.objects.filter(compte=pk)
    except:
        raise Http404("Le Budget spécifié n'existe pas!")
    return render(request, "compta/detail_budget.html", {'budget': budget, 'transac':transac})

def export_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'

    writer = csv.writer(response)
    transac = [[t.nom, datetime.strftime(t.date,"%d.%m.%y"), str(t.somme), t.compte.nom, t.budget.nom if t.budget is not None else str(None), t.description.replace("\r\n"," ")] for t in Transaction.objects.all()]
    writer.writerows(transac)


    return response