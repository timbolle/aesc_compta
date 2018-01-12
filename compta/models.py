from django.db import models
from django.dispatch import receiver
from datetime import datetime

def facture_path(instance, filename):
    print(instance.id)
    return 'factures/{0}/{1}'.format(instance.id,filename)

class Compte(models.Model):
    nom = models.CharField(max_length = 140)
    somme_depart = models.DecimalField( max_digits=11, decimal_places=2)
    somme_actuelle = models.DecimalField(max_digits=11, decimal_places=2)

    @property
    def url(self):
        return "/compte/"+str(self.pk)


    def __str__(self):
        return self.nom

class Budget(models.Model):
    nom = models.CharField(max_length = 140)
    somme_depart = models.DecimalField(max_digits=11, decimal_places=2)
    somme_actuelle = models.DecimalField(max_digits=11, decimal_places=2)

    @property
    def url(self):
        return "/compte/"+str(self.pk)

    def __str__(self):
        return self.nom

class Transaction(models.Model):
    nom = models.CharField(max_length=140)
    somme = models.DecimalField(max_digits=11, decimal_places=2)
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField()
    date_traitement = models.DateField(default=datetime.now)
    description = models.TextField()

    facture = models.FileField(upload_to=facture_path, blank=True, null=True)

    def __str__(self):
        return self.nom

# Faudra regarder pour les transitoire comment faire
# Est ce qu'on fait des vrais transitoires, dans ce cas regardera quand fera un truc de cloture des comptes
# Si fait en sort que prenne en compte le retour attendu sur un achat, devra peut être regarder plus tot

@receiver(models.signals.post_save, sender=Transaction)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        c = Compte.objects.get(nom=instance.compte)
        c.somme_actuelle += instance.somme  # change field
        c.save()  # this will update only
        if  instance.budget:
            b = Budget.objects.get(nom=instance.budget)
            b.somme_actuelle += instance.somme  # change field
            b.save()  # this will update only

@receiver(models.signals.pre_delete, sender=Transaction)
def execute_before_delete(sender, instance, using, *args, **kwargs):
    c = Compte.objects.get(nom=instance.compte)
    c.somme_actuelle -= instance.somme  # change field
    c.save()  # this will update only
    if instance.budget:
        b = Budget.objects.get(nom=instance.budget)
        b.somme_actuelle -= instance.somme  # change field
        b.save()  # this will update only


