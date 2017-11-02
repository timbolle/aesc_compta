from django.db import models

class Compte(models.Model):
    nom = models.CharField(max_length = 140)
    somme_depart = models.DecimalField( max_digits=11, decimal_places=2)
    somme_actuelle = models.DecimalField(max_digits=11, decimal_places=2)
    # somme_depart = models.FloatField()
    # somme_actuelle = models.FloatField()

    def __str__(self):
        return self.nom

class Budget(models.Model):
    nom = models.CharField(max_length = 140)
    somme_depart = models.DecimalField(max_digits=11, decimal_places=2)
    somme_actuelle = models.DecimalField(max_digits=11, decimal_places=2)
    # somme_depart = models.FloatField()
    # somme_actuelle = models.FloatField()


    def __str__(self):
        return self.nom

class Transaction(models.Model):
    nom = models.CharField(max_length=140)
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    somme = models.DecimalField(max_digits=11, decimal_places=2)
    date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return self.nom
