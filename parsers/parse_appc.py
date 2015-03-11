# -*- coding: utf-8 -*-
import logging
import re
from utils import mongo
from utils import entity_resolver


class AppcParser:
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.resolver = entity_resolver.MasterEntitiesResolver()
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "appc_parse"

    def run(self):
        self._logger.debug("\n\nParsing APPC")
        all_entries = self.db.fetch_all("appc_scrape", paged=False)
        for document in all_entries:
            name = self._normalize_text(document["name"])
            self._logger.debug("\nLobbying Firm: %s" % name)
            meta = document["meta"]
            meta["date_range"] = {
                "to": document["date_to"],
                "from": document["date_from"]
            }
            clients = self._parse_clients(document["clients"])
            staff = self._parse_staff(document["staff"])
            countries = self._parse_countries(document["countries"])
            entry = {
                "lobbyist": {
                    "name": name,
                    "contact_details": document["contacts"],
                    "address": document["addresses"],
                    "pa_contact": self._fill_empty_field("pa_contact", document)
                },
                "clients": clients,
                "staff": staff,
                "countries": countries,
                "meta": document["meta"]
            }
            self.db.save(self.COLLECTION_NAME, entry)

    def _parse_clients(self, clients):
        self._logger.debug("... Parsing Clients")
        types = ["monitoring", "consultancy", "pro-bono"]
        client_list = []
        for client_type in types:
            for client in clients[client_type]:
                self._logger.debug("* %s" % self._normalize_text(client["name"]))
                entry = {
                    "name": self._normalize_text(client["name"]),
                    "client_type": client_type,
                    "description": client["description"]

                }
                client_list.append(entry)
        return client_list

    def _parse_staff(self, staff):
        self._logger.debug("... Parsing Staff")
        types = ["has_pass", "no_pass"]
        staff_list = []
        for staff_type in types:
            for entry in staff[staff_type]:
                print "~", self._normalize_text(entry)
                entry = {
                    "name": self._normalize_text(entry),
                    "staff_type": staff_type
                }
                staff_list.append(entry)
        return staff_list

    def _parse_countries(self, countries):
        self._logger.debug("... Parsing Staff")
        return [self._normalize_text(x) for x in countries]

    @staticmethod
    def _normalize_text(text, capitalize=True):
        text = text.rstrip(".").strip()
        if ", The" == text[-5:]:
            text = u"The {0}".format(text.strip(", The"))
        if "  " in text:
            text = text.replace("  ", " ")
        if capitalize:
            if text.isupper():
                text = text.title()
        if len(text) > 1:
            if text[1] == "-":
                text = text.lstrip("-")
            if text[:2] == "- ":
                text = text.lstrip("-")
        return text.strip()

    @staticmethod
    def _fill_empty_field(field, document):
        return None if field not in document else document[field]



