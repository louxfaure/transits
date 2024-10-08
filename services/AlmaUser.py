# -*- coding: utf-8 -*-

# external imports
import logging
import xml.etree.ElementTree as ET
from math import *
from . import Alma_api_fonctions


class AlmaUser(object):
    """ Remonte un utilisateur via son primary_id"""

    def __init__(
        self,
        user_id,
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
            "https://api-eu.hosted.exlibrisgroup.com/almaws/v1/users/{}?user_id_type=all_unique&view=brief&expand=none".format(user_id),
            accept=accept,
        )
        # self.response = self.appel_api.extract_content(response)
        if status == "Error":
            self.est_erreur = True
            self.message_erreur = response
        else:
            self.record = self.appel_api.extract_content(response)
            self.mes_logs.debug(self.record)


    def user_name(self):
        return self.record["full_name"]
    
    def barcode(self):
        for user_id in self.record["user_identifier"] :
            if user_id['id_type']['value'] == 'BARCODE' :
                return user_id['value']
        return user_id['primary_id']

    