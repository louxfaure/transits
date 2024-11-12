from django.http import HttpResponse, JsonResponse,  Http404, HttpResponseRedirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.templatetags.static import static
from collections import defaultdict
from .services import AlmaSet
from .models import Parametres
import json
import logging
import csv
import tempfile, os

#Initialisation des logs
mes_logs = logging.getLogger(__name__)
@login_required
def transits(request):
    return render(request, 'transits.html')  # Rendu du gabarit HTML sans données

    

@login_required
def transits_data(request):
    api_key = settings.ALMA_API_KEY['CASIERS_UB']
    # Identifiant du jeux de résultat listant les documents en transi vers Marne
    set_id = Parametres.objects.get( clef_parametre = 'set_id')

    ######################################################
    # Récupéraion de la liste des exemplaires en transit #
    ######################################################
    mon_set = AlmaSet.AlmaSet(apikey=api_key,service=__name__,set_id=set_id)
    datas = mon_set.liste_transit_pour_marne

    ###################################################
    # Formatage des données pour affichage sur la vue #
    ###################################################
    # On crée une structure hiérarchique avec defaultdict
    gestion_structure = defaultdict(lambda: defaultdict(list))

    # On remplit la structure et on comptabilise le nombre d'items
    gestion_item_count = defaultdict(int)

    # Variable de contrôle pour voir s'il y a des doc pour les casiers Marne
    docs_pour_Marne = False

    # On remplit la structure
    for entry in datas:
        mes_logs.debug("entry")
        mes_logs.debug(entry)
        gestion_nom = entry['bib_gestion_nom']
        retrait_nom = entry['bib_retrait_nom']
        if  entry['Marne'] : docs_pour_Marne = True
        # On enlève les informations liées à la gestion et au retrait pour ne garder que les items
        item = {
            "bib_retrait": entry["bib_retrait"],
            "etape_traitement_demande": entry["etape_traitement_demande"],
            "type_de_demande": entry["type_de_demande"],
            "titre": entry["titre"],
            "cb": entry["cb"]
        }
        #
        # On ajoute l'item sous le bon bib_gestion_nom et bib_retrait_nom
        gestion_structure[gestion_nom][retrait_nom].append(item)

        # On augmente le compteur d'items pour ce bib_gestion_nom
        gestion_item_count[gestion_nom] += 1

    # Reformater la structure pour obtenir le format souhaité
    result = [
        {
            "bibliotheque_retrait": gestion,
            "nombre_doc_a_prendre_en_charge": gestion_item_count[gestion],
            "bibliotheque_destination": [
                {
                    "nom": retrait,
                    "items": items
                }
                for retrait, items in retraits.items()
            ]
        }
        for gestion, retraits in gestion_structure.items()
    ]

    mes_logs.debug(json.dumps(result,indent=4))
    
    #####################################################
    # Création du fichier CSV pour chargement du casier #
    #####################################################

    file_url = ""
    if docs_pour_Marne:
        # Nom du fichier
        filename = "export.csv"
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        # Générer le fichier CSV et le sauvegarder
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter='|')
            writer.writerow(["N° carte", "Code barres", "Adhérent", "Titre"])
            for demande in datas:
                if demande['Marne']:
                    writer.writerow([demande['N° carte'],demande['cb'],demande['Adhérent'],demande['titre']])

            mes_logs.info(f"Fichier {file_path} créé avec succès.")
        # Crée un lien pour télécharger le fichier
        file_url = os.path.join(settings.MEDIA_URL, filename)
   

    return JsonResponse({'data': result, 'file_url': file_url, 'docs_pour_Marne':docs_pour_Marne }, safe=False)
    # return render(request, "transits/transits.html", {'data': result, 'file_url': file_url, 'docs_pour_Marne':docs_pour_Marne })

def transits_csv(request):
    mes_logs.debug("CSV CSV CSC")
    api_key = settings.ALMA_API_KEY['CASIERS_UB']
    # Identifiant du jeux de résultat listant les documents en transi vers Marne
    set_id = Parametres.objects.get( clef_parametre = 'set_id')

    ######################################################
    # Récupéraion de la liste des exemplaires en transit #
    ######################################################
    mon_set = AlmaSet.AlmaSet(apikey=api_key,service=__name__,set_id=set_id)
    datas = mon_set.liste_transit_pour_marne

    #####################################################
    # Création du fichier CSV pour chargement du casier #
    #####################################################
    # Nom du fichier
    filename = "export.csv"
    file_path = os.path.join(settings.MEDIA_ROOT, filename)

    # Générer le fichier CSV et le sauvegarder
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter='|')
        writer.writerow(["N° carte", "Code barres", "Adhérent", "Titre"])
        for demande in datas:
            if demande['Marne']:
                writer.writerow([demande['N° carte'],demande['cb'],demande['Adhérent'],demande['titre']])

        mes_logs.info(f"Fichier {file_path} créé avec succès.")
    with open(file_path) as myfile:
        response = HttpResponse(myfile, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
        return response

