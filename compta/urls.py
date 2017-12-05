from django.conf.urls import url
from . import views
from django.views.generic import ListView, DetailView
from compta.models import Compte, Budget, Transaction


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^hello$', views.hello, name='hello'),
    url(r'^comptes$', ListView.as_view(
                        queryset=Compte.objects.all().order_by("nom"),
                        template_name="compta/compte.html")),
    url(r'^budgets$', ListView.as_view(
                        queryset=Budget.objects.all().order_by("nom"),
                        template_name="compta/budget.html")),
    url(r'^transactions$', ListView.as_view(
                        queryset=Transaction.objects.all().order_by("-date"),
                        template_name="compta/transaction.html")),
    url(r'^compte/(?P<pk>\d+)$', views.detail_compte),
    url(r'^budget/(?P<pk>\d+)$', views.detail_budget),
    url(r'^export2', views.export_csv, name="export_csv"),
    url(r'^export', views.export, name="export"),
]