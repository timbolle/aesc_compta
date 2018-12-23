from compta.models import Transaction, Compte, Budget


def update_budget_and_comptes():
    # For budgets
    for b in Budget.objects.all():
        delta_somme = sum([t.somme for t in Transaction.objects.filter(budget=b.id)])
        b.somme_actuelle = float(b.somme_depart) + float(delta_somme)
        b.save()

    # For Comptes
    for c in Compte.objects.all():
        delta_somme = sum([t.somme for t in Transaction.objects.filter(compte=c.id)])
        c.somme_actuelle = float(c.somme_depart) + float(delta_somme)
        c.save()

