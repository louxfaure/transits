from django.contrib import admin
from .models import Bibliotheque, Parametres


@admin.register(Bibliotheque)
class BibliothequeAdmin(admin.ModelAdmin):
    list_display = ('library_id', 'library_name')
    ordering = ('library_name','library_id')
    search_fields = ('library_id', 'library_name')

@admin.register(Parametres)
class ParametresAdmin(admin.ModelAdmin):
    list_display = ('clef_parametre', 'nom_parametre', 'valeur_parametre')
    ordering = ('clef_parametre','nom_parametre')
    search_fields = ('clef_parametre','nom_parametre')
