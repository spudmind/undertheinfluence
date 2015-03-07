# -*- coding: utf-8 -*-
import logging
import re
from utils import mongo
from utils import entity_resolver


class PrcaParser:
    def __init__(self):
        self._logger = logging.getLogger('spud')

    def run(self):
        self.resolver = entity_resolver.MasterEntitiesResolver()
        self.db = mongo.MongoInterface()
        self._logger.debug("Parsing PRCA")
        all_entries = self.db.fetch_all('prca_scrape', paged=False)

        for document in all_entries:
            name = self._normalize_text(document["name"])
            self._logger.debug("\n... %s" % name)
            meta = document["meta"]
            meta["date_range"] = {
                "to": document["date_to"],
                "from": document["date_from"]
            }
            if "clients" in document:
                self._parse_clients(document["clients"])
            entry = {
                "lobbyist": {
                    "name": name,
                    "contact_details": " ".join(document["contact"]),
                    "pa_contact": self._fill_empty_field("pa_contact", document)
                },
                "clients": self._fill_empty_field("clients", document),
                "staff": self._fill_empty_field("staff", document),
                "meta": document["meta"]
            }
            #self.db.save("prca_parse", entry)

    def _parse_clients(self, clients):
        client_count = len(clients)
        lengths = [len(c) for c in clients]
        average = sum(lengths ) / client_count
        print "client count:", client_count
        print "average field:", average
        print "min - max:", min(lengths), "-", max(lengths)
        print "-"
        for entry in clients:
            if self._has_data(entry):
                entry = self._normalize_text(entry, capitialize=False)
                print "*", entry

    def _normalize_text(self, text, capitialize=True):
        text = self._strip_parentheses(text)
        if capitialize:
            if text.isupper():
                text = text.title()
        return text

    @staticmethod
    def _has_data(text):
        result = True
        checks = [
            "Address:", "Website:", "Email:", "www.", "Telephone:",
            "@", "http:", "Employer:", "Employer:", "Job Title:",
            "comprising:"
        ]
        for test in checks:
            if test in text:
                result = False
        return result



    @staticmethod
    def _fill_empty_field(field, document):
        return None if field not in document else document[field]

    @staticmethod
    def _strip_parentheses(text):
        return re.sub('\(.+?\)\s*', '', text)




