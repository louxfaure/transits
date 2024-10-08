# -*- coding: utf-8 -*-
import time
import math
import re
import json
import logging
from math import *
from . import Alma_api_fonctions, AlmaRequests
from concurrent.futures import ThreadPoolExecutor, as_completed



class AlmaSet(object):
    """Interagie avaec un ensemble de résultat """

    def __init__(
        self, apikey="", service="", set_id=""
    ):
        if apikey is None:
            raise Exception("Merci de fournir une clef d'APi")
        self.apikey = apikey
        self.service = service
        self.set_id = set_id
        self.est_erreur = False
        self.mes_logs = logging.getLogger(__name__)
        self.nombre_de_membres = ""
        self.liste_transit_pour_marne = []
        self.accept = "json"
        self.est_erreur = False
        self.message_erreur = ""
        self.appel_api = Alma_api_fonctions.Alma_API(
            apikey=self.apikey, service=self.service
        )
        
        if not self.est_erreur:
            self.liste_des_membres()

    def get_set(self):
        status, response = self.appel_api.request(
            "GET",
            "https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/sets/{}".format(
                self.set_id
            ),
            accept=self.accept,
        )
        if status == "Error":
            self.est_erreur = True
            self.message_erreur = response
        else:
            set_data = self.appel_api.extract_content(response)
            return set_data

    def get_nombre_de_membres(self):
        set_info = self.get_set()
        return set_info["number_of_members"]["value"]

    def get_set_members(self, set_id, limit, offset):
        status, response = self.appel_api.request(
            "GET",
            "https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/sets/{}/members?limit={}&offset={}".format(
                set_id, limit, offset
            ),
            accept=self.accept,
        )
        if status == "Error":
            return True, response
        else:
            return False, self.appel_api.extract_content(response)

    def liste_des_membres(self):
        """Récupère la liste des documents dans un set
        - récupère la liste des membres
        - pour chaque document récupère des informations détaillées
        """
        # On évalue le nombre d'appels nécessaires pour obtenir la liste
        nb_appels = math.ceil(self.get_nombre_de_membres() / 100)
        all_documents = []

        for i in range(0, nb_appels):
            offset = i * 100
            status, result = self.get_set_members(
                set_id=self.set_id, limit=100, offset=offset
            )
            self.mes_logs.debug(result)
            if status == "Error":
                self.est_erreur = True
                self.message_erreur = result
            else:
                all_documents.extend(result["member"])

        # for doc in all_documents :
        #     self.mes_logs.info("Récupération des infos pour le mmsid {}".format(doc["id"]))
        #     pattern = r"bibs/(\d+)/holdings/(\d+)/items/(\d+)"
        #     match = re.search(pattern, doc["link"])
        #     mms_id = match.group(1)
        #     holding_id = match.group(2)
        #     item_id = match.group(3)
        #     demandes = AlmaRequests.AlmaRequests(mms_id=mms_id,holding_id=holding_id,item_id=item_id,apikey=self.apikey,service=self.service)
        #     if demandes.nb_de_demandes() > 0 :
        #          self.liste_transit_pour_marne.append(demandes.repere_transit_pour_marne())



        def fetch_details(doc):
            self.mes_logs.info("Récupération des infos pour le mmsid {}".format(doc["id"]))
            pattern = r"bibs/(\d+)/holdings/(\d+)/items/(\d+)"
            match = re.search(pattern, doc["link"])
            mms_id = match.group(1)
            holding_id = match.group(2)
            item_id = match.group(3)
            demandes = AlmaRequests.AlmaRequests(mms_id=mms_id,holding_id=holding_id,item_id=item_id,apikey=self.apikey,service=self.service)
            if demandes.nb_de_demandes() > 0 :
                return demandes.repere_transit_pour_marne()


        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = {executor.submit(fetch_details, doc): doc for doc in all_documents}

            for future in as_completed(futures):
                result = future.result()
                self.mes_logs.debug(result)
                if result:
                    self.liste_transit_pour_marne.append(result)
