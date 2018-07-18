from django.db import models
from django.dispatch import receiver
from datetime import datetime
from django.shortcuts import get_object_or_404

def facture_path(instance, filename):
    print(instance.numero)
    return 'factures/{0}/{1}'.format(instance.numero,filename)

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

class Meta_Stuff(models.Model):
    # only one instance
    transac_number = models.IntegerField(default=1)

    def __str__(self):
        return self.transac_number

    @classmethod
    def get_lastnumber(cls, default=1):
        return cls.objects.get(pk=1).transac_number
        # number = get_object_or_404(cls, pk=default)
        # return number.transac_number

    @classmethod
    def increment_lastnumber(cls):
        new = cls.objects.get(pk=1)
        new.transac_number += 1
        new.save()

    @classmethod
    def decrement_lastnumber(cls):
        new = cls.objects.get(pk=1)
        if new.transac_number >1:
            new.transac_number -= 1
            new.save()


class Transaction(models.Model):
    numero = models.IntegerField(default=Meta_Stuff.get_lastnumber)
    # numero = models.IntegerField(default=Meta_Stuff.objects.first().transac_number)
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

    def facture_name(self):
        return self.facture.name.split('/')[-1]





@receiver(models.signals.post_save, sender=Transaction)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        ## transac number
        Meta_Stuff.increment_lastnumber()

        ## current Compte/budget
        c = Compte.objects.get(nom=instance.compte)
        c.somme_actuelle += instance.somme  # change field
        c.save()  # this will update only
        if  instance.budget:
            b = Budget.objects.get(nom=instance.budget)
            b.somme_actuelle += instance.somme  # change field
            b.save()  # this will update only

@receiver(models.signals.pre_delete, sender=Transaction)
def execute_before_delete(sender, instance, using, *args, **kwargs):
    ## transac number
    Meta_Stuff.decrement_lastnumber()

    ## current Compte/budget
    c = Compte.objects.get(nom=instance.compte)
    c.somme_actuelle -= instance.somme  # change field
    c.save()  # this will update only
    if instance.budget:
        b = Budget.objects.get(nom=instance.budget)
        b.somme_actuelle -= instance.somme  # change field
        b.save()  # this will update only


