from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.http import HttpResponse, Http404
from compta.models import Transaction, Compte, Budget
import csv, xlwt, re
from datetime import datetime
from django.contrib.auth.decorators import login_required
from compta.export import Export


def hello(request):
    return HttpResponse("<h2>HEY! you</h2>")

@login_required
def index(request):
    return render(request, 'compta/home.html')

@login_required
def detail_compte(request, pk):
    try:
        compte = Compte.objects.get(pk=pk)
        transac = Transaction.objects.filter(compte=pk)
    except:
        raise Http404("Le compte spécifié n'existe pas!")
    return render(request, "compta/detail_compte.html", {'compte': compte, 'transac':transac})

@login_required
def detail_budget(request, pk):
    try:
        budget = Budget.objects.get(pk=pk)
        transac = Transaction.objects.filter(budget=pk)
    except:
        raise Http404("Le Budget spécifié n'existe pas!")
    return render(request, "compta/detail_budget.html", {'budget': budget, 'transac':transac})

class ListingView(ListView):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@login_required
def export(request):
    export_type = request.GET.get('type', '')
    ref = request.GET.get('origin', '').strip("/")
    try:
        request.META["HTTP_REFERER"]
    except:
        raise Http404("NOT OK!! GET OUT --> [1]")

    if re.match(r'(compte/\d+)|(budget/\d+)|transactions',ref) is None or export_type not in ["CSV","Excel","PDF"]:
        raise Http404("NOT OK!! GET OUT --> [2]")

    if re.match(r'transactions', ref):
        # prend  pour tous les comptes et budgets
        comptes = Compte.objects.all()
        budgets = Budget.objects.all()
        exp = Export(comptes, budgets)


    elif re.match(r'compte/\d+', ref):
        pk = int(re.match(r"compte/(?P<pk>\d+)", ref)["pk"])
        comptes = Compte.objects.filter(pk= pk)
        exp = Export(comptes=comptes)

    elif re.match(r'budget/\d+', ref):
        pk = int(re.match(r"budget/(?P<pk>\d+)", ref)["pk"])
        budgets = Budget.objects.filter(pk= pk)
        exp = Export(budgets=budgets)

    else:
        raise Http404("NOT OK!! GET OUT --> [3]")

    if export_type == "CSV":
        reponse = exp.generate_csv()
        return reponse
    elif export_type == "Excel":
        reponse = exp.generate_excel()
        return reponse
    elif export_type == "PDF":
        response = exp.generate_pdf()
        return response


    to_print = "<h2>{} {}</h2>".format(export_type, request.META["HTTP_REFERER"])
    return HttpResponse(to_print)

