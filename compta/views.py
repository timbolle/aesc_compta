from django.shortcuts import render
from django.http import HttpResponse, Http404
from compta.models import Transaction, Compte, Budget
import csv, xlwt
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

def export_csv(data):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'

    writer = csv.writer(response)
    if "comptes" in data.keys():
        writer.writerow(["Comptes","Somme Initiale", "Somme Actuelle"])
        writer.writerows(list(zip(data["comptes"], data["comptes_solde_ini"], data["comptes_solde_actu"])))
        writer.writerow([])
    if "budgets" in data.keys():
        writer.writerow(["Budgets","Somme Initiale", "Somme Actuelle"])
        writer.writerows(list(zip(data["budgets"], data["budgets_solde_ini"], data["budgets_solde_actu"])))
        writer.writerow([])
    writer.writerow(["nom", "date", "montant", "compte", "budget", "description"])
    writer.writerows(data["transactions"])

    return response

def export_excel(data):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="export.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Résumé')

    # Sheet header, first row
    row_num = 0


    if "comptes" in data.keys():
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ["Comptes","Somme Initiale", "Somme Actuelle"]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        for row in zip(data["comptes"], data["comptes_solde_ini"], data["comptes_solde_actu"]):
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
        row_num += 1
    if "budgets" in data.keys():
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        row_num += 1 if "comptes" in data.keys() else 0
        columns = ["Budgets","Somme Initiale", "Somme Actuelle"]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        for row in zip(data["budgets"], data["budgets_solde_ini"], data["budgets_solde_actu"]):
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
        row_num +=1

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    row_num += 1
    columns = ["nom", "date", "montant", "compte", "budget", "description"]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    for row in data["transactions"]:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


def export(request):
    export_type = request.GET.get('type', '')
    try:
        ref = request.META["HTTP_REFERER"].split("/")[-1]
    except:
        raise Http404("NOT OK!! GET OUT --> []")

    if ref not in ["comptes","budgets","transactions"] or export_type not in ["CSV","Excel","PDF"]:
        raise Http404("NOT OK!! GET OUT --> []")

    data={} # contiendra une somme de depart, une somme actuelle et une liste de transactions
    if ref == "transactions":
        # prend  pour tous les comptes
        comptes = Compte.objects.all()
        budgets = Budget.objects.all()
        data["comptes"] = [c.nom for c in comptes]+["+".join([c.nom for c in comptes])]
        data["comptes_solde_ini"] = [c.somme_depart for c in comptes]+[sum([c.somme_depart for c in comptes])]
        data["comptes_solde_actu"] = [c.somme_actuelle for c in comptes]+[sum([c.somme_actuelle for c in comptes])]

        data["budgets"] = [c.nom for c in budgets]+["+".join([c.nom for c in budgets])]
        data["budgets_solde_ini"] = [c.somme_depart for c in budgets]+[sum([c.somme_depart for c in budgets])]
        data["budgets_solde_actu"] = [c.somme_actuelle for c in budgets]+[sum([c.somme_actuelle for c in budgets])]

        data["transactions"] = [[t.nom, datetime.strftime(t.date,"%d.%m.%y"), str(t.somme), t.compte.nom, t.budget.nom if t.budget is not None else str(None), t.description.replace("\r\n"," ")] for t in Transaction.objects.all()]

    if export_type == "CSV":
        reponse = export_csv(data)
        return reponse
    elif export_type == "Excel":
        reponse = export_excel(data)
        return reponse


    to_print = "<h2>{} {}</h2>".format(export_type, request.META["HTTP_REFERER"])
    return HttpResponse(to_print)
