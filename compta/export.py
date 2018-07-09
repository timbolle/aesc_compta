from compta.models import Transaction, Compte, Budget
from django.db.models import Q
from django.template.loader import render_to_string
from django.conf import settings
import csv, xlwt, subprocess, os
from datetime import datetime
from django.http import HttpResponse, Http404

class Export():

    def __init__(self, comptes=None, budgets=None):
        self.comptes = comptes
        self.budgets = budgets

        compte_pk_list = self.comptes.values("pk") if self.comptes else []
        budget_pk_list = self.budgets.values("pk") if self.budgets else []
        self.transac = Transaction.objects.filter(Q(compte__in= compte_pk_list) or Q(budget__in= budget_pk_list))

    def get_output(self, obj="C"):
        """
        Prepare the output of compte / budget
        :param obj: "C" for compte (default) and "B" for budget
        :return: a generator with tuple (name, somme_depart, somme_actuelle, difference) for each compte/budget and the total
        """
        if obj in ["C", "c"]:
            obj = self.comptes
        elif obj in ["B", "b"]:
            obj = self.budgets
        else:
            raise(Exception("Invalid parameter"))

        for c in obj:
            yield (c.nom, c.somme_depart, c.somme_actuelle, c.somme_actuelle - c.somme_depart)


    def get_total(self, obj= "C"):
        """
        get the total for compte or budget
        :param obj:
        :return:
        """
        if obj in ["C", "c"]:
            obj = self.comptes
        elif obj in ["B", "b"]:
            obj = self.budgets
        else:
            raise(Exception("Invalid parameter"))

        tot_depart = Export.sum_queryset(obj.values_list("somme_depart"))
        tot_actuelle = Export.sum_queryset(obj.values_list("somme_actuelle"))
        return ("Total", tot_depart, tot_actuelle, tot_actuelle-tot_depart)

    def generate_data(self):
        self.context = {}
        if self.comptes:
            self.context["comptes"] = self.get_output("C")
            self.context["total_compte"] = self.get_total("C")
        if self.budgets:
            self.context["budgets"] = self.get_output("B")
            self.context["total_budget"] = self.get_total("B")
        self.context["transac"] = self.transac
        self.context["total_entree"] = Export.sum_queryset(self.transac.filter(somme__gt= 0).values_list("somme"))
        self.context["total_depense"] = Export.sum_queryset(self.transac.filter(somme__lt= 0).values_list("somme"))


    def generate_html(self):
        self.generate_data()
        content = render_to_string('compta/export_template.html', self.context)
        with open(Export.get_html_path() ,"w", encoding='utf-8') as f:
            f.write(content)

    def generate_pdf(self):
        self.generate_html()
        command = "{} {} {}".format(r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe", Export.get_html_path(), Export.get_pdf_path())
        # command = "{} {} {}".format(r"E:\Wkhtmltopdf\bin\wkhtmltopdf.exe", Export.get_html_path(), Export.get_pdf_path())
        print(command)
        subprocess.run(command)
        response = HttpResponse( open(Export.get_pdf_path(), "rb") ,content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="export.pdf"'

        return response


    def pretty_transac(self):
        self.context["transac"] = []
        for t in self.transac:
            temp = [t.numero, t.nom, datetime.strftime(t.date,"%Y-%m-%d"), datetime.strftime(t.date_traitement,"%Y-%m-%d"),
                    t.somme, t.compte.nom, t.budget.nom if t.budget != None else None, t.description, t.facture.name ]
            self.context["transac"].append(temp)

    def generate_csv(self):
        self.generate_data()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'

        writer = csv.writer(response)
        if self.comptes:
            writer.writerow(["Comptes", "Somme Initiale", "Somme Actuelle", "difference"])
            writer.writerows(self.context["comptes"])
            writer.writerow(self.context["total_compte"])

        if self.budgets:
            writer.writerow(["Budgets", "Somme Initiale", "Somme Actuelle", "difference"])
            writer.writerows(self.context["budgets"])
            writer.writerow(self.context["total_budget"])

        writer.writerow(["numero", "nom", "date", "date_traitement", "montant", "compte", "budget", "description","facture"])
        self.pretty_transac()
        writer.writerows(self.context["transac"])
        writer.writerow(["total_depenses", "total_entrees"])
        writer.writerow([self.context["total_depense"], self.context["total_entree"]])

        return response

    def generate_excel(self):
        self.generate_data()
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="export.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Bilan')

        row_num = 0

        if self.comptes:
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ["Comptes", "Somme Initiale", "Somme Actuelle", "Différence"]
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            # Sheet body, remaining rows
            font_style = xlwt.XFStyle()
            for row in self.context["comptes"]:
                row_num += 1
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style)
            font_style.font.bold = True
            row_num += 1
            for col_num, col in enumerate(self.context["total_compte"]):
                ws.write(row_num, col_num, col, font_style)
            row_num += 2

            if self.budgets:
                font_style = xlwt.XFStyle()
                font_style.font.bold = True
                columns = ["Budget", "Somme Initiale", "Somme Actuelle", "Différence"]
                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)
                # Sheet body, remaining rows
                font_style = xlwt.XFStyle()
                for row in self.context["budgets"]:
                    row_num += 1
                    for col_num in range(len(row)):
                        ws.write(row_num, col_num, row[col_num], font_style)
                font_style.font.bold = True
                row_num += 1
                for col_num, col in enumerate(self.context["total_compte"]):
                    ws.write(row_num, col_num, col, font_style)
                row_num += 2

            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            row_num += 1
            columns = ["numero", "nom", "date", "date_traitement", "montant", "compte", "budget", "description","facture"]
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            # Sheet body, remaining rows
            font_style = xlwt.XFStyle()
            self.pretty_transac()
            for row in self.context["transac"]:
                row_num += 1
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style)

            row_num += 1
            font_style.font.bold = True
            ws.write(row_num, 0, "Total_depenses", font_style)
            ws.write(row_num, 1, self.context["total_depense"], font_style)
            row_num += 1
            ws.write(row_num, 0, "Total_entree", font_style)
            ws.write(row_num, 1, self.context["total_entree"], font_style)

            wb.save(response)
            return response

    @staticmethod
    def sum_queryset(qs):
        """
        Compute the sum on a query set (list of tuple)
        :param qs: List of tuples (QuerySet)
        :return: the sum
        """
        return sum(map( lambda x: x[0], qs))

    @staticmethod
    def get_html_path():
        return os.path.normcase(os.path.join(settings.MEDIA_ROOT, "export/export.html"))

    @staticmethod
    def get_pdf_path():
        return os.path.normcase(os.path.join(settings.MEDIA_ROOT, "export/export.pdf"))


if __name__ == '__main__':
    pass