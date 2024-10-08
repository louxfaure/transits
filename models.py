from django.db import models

class Bibliotheque(models.Model):
    library_name = models.CharField(max_length=200,verbose_name=u"Nom de la bibliotheque")
    library_id = models.CharField(max_length=10,verbose_name=u"Identifiant Alma de la bibliotheque",unique=True)

    def __str__(self):
        return self.library_name

class Parametres(models.Model):
    clef_parametre = models.CharField(max_length=50,verbose_name=u"Code du paramètre",unique=True)
    nom_parametre = models.CharField(max_length=250,verbose_name=u"Description du paramètre")
    valeur_parametre = models.CharField(max_length=50,verbose_name=u"Valeur du paramètre")

    def __str__(self):
        return self.valeur_parametre