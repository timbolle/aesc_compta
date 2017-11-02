from django.contrib import admin
from compta.models import Compte, Budget, Transaction

admin.site.register(Compte)
admin.site.register(Budget)
admin.site.register(Transaction)
# Register your models here.
