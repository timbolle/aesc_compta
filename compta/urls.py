from django.conf.urls import url
from . import views
from django.views.generic import ListView, DetailView
from compta.models import Compte, Budget, Transaction


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^hello$', views.hello, name='hello'),
    url(r'^comptes$', views.ListingView.as_view(
                        queryset=Compte.objects.all().order_by("nom"),
                        template_name="compta/compte.html")),
    url(r'^budgets$', views.ListingView.as_view(
                        queryset=Budget.objects.all().order_by("nom"),
                        template_name="compta/budget.html")),
    url(r'^transactions$', views.transactions, name="transactions"),
    url(r'^compte/(?P<pk>\d+)$', views.detail_compte, name="detail_compte"),
    url(r'^budget/(?P<pk>\d+)$', views.detail_budget, name="detail_budget"),
    url(r'^export', views.export, name="export"),
]