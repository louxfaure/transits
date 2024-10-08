# -*- coding: utf-8 -*-

# external imports
import json
import logging
import xml.etree.ElementTree as ET
from math import *
from . import Alma_api_fonctions, AlmaUser
from ..models import Bibliotheque


class AlmaRequests(object):
    """ Remonte  les demandes portées sur un exemplaire"""

    def __init__(
        self,
        mms_id,
        holding_id,
        item_id,
        request_type = "HOLD",
        status = "active",
        accept="json",
        apikey="",
        service="",
    ):
        if apikey is None:
            raise Exception("Merci de fournir une clef d'APi")
        self.apikey = apikey
        self.service = service
        self.est_erreur = False
        self.mes_logs = logging.getLogger(__name__)
        self.appel_api = Alma_api_fonctions.Alma_API(
            apikey=self.apikey, service=self.service
        )
        status, response = self.appel_api.request(
            "GET",
            "https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/holdings/{}/items/{}/requests?&status={}".format(mms_id,holding_id,item_id,status),
            accept=accept,
        )
        # self.response = self.appel_api.extract_content(response)
        if status == "Error":
            self.est_erreur = True
            self.message_erreur = response
        else:
            self.record = self.appel_api.extract_content(response)
            self.mes_logs.debug(json.dumps(self.record,indent=4))


    def nb_de_demandes(self):
        return int(self.record["total_record_count"])

    def repere_transit_pour_marne(self):
        for demande in self.record['user_request'] :
            if 'pickup_location_library' not in demande :
                self.mes_logs.error(demande)
                continue
            if 'task_name' not in demande :
                continue
            self.mes_logs.debug(demande)
            bib_retrait = demande.get('pickup_location_library', 0)
            bib_retrait_nom = demande.get('pickup_location', 0)
            bib_gestion = demande.get('managed_by_library_code',0)
            bib_gestion_nom = demande.get('managed_by_library',0)
            etape_traitement_demande = demande.get('task_name',0)
            type_de_demande = demande['request_sub_type']['value']
            titre = demande['title']
            cb = demande['barcode']
            if etape_traitement_demande == 'Transit Item' and demande['pickup_location_library'] != demande['managed_by_library_code'] and Bibliotheque.objects.filter(library_id=bib_gestion).exists():
                infos_transit = {
                    'bib_retrait':bib_retrait,
                    'bib_retrait_nom':bib_retrait_nom,
                    'bib_gestion':bib_gestion,
                    'bib_gestion_nom':bib_gestion_nom,
                    'etape_traitement_demande':etape_traitement_demande,
                    'type_de_demande':type_de_demande,
                    'titre':titre,
                    'cb':cb,
                    'Marne':False
                }
                # Si transit pour Marne on récupère des infos supplémentaires pour générer le fichier
                if bib_retrait =='1602000000' and type_de_demande == 'PATRON_PHYSICAL':
                    #On récupère le nom et le code barre de l'utilisateur
                    user_primary_id = demande['user_primary_id']
                    user = AlmaUser.AlmaUser(user_id=user_primary_id,apikey=self.apikey,service=self.service)
                    user_name = user.user_name()
                    cb_user = user.barcode()
                    # Si l'utilisateur n'a pas de CB on envoie pas la résas à l'automate
                    if cb_user : 
                            infos_transit['Marne'] = True,   
                            infos_transit['N° carte'] = cb_user
                            infos_transit['Adhérent'] = user_name
                return infos_transit