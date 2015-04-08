# -*- coding: utf-8 -*-
import logging
from utils import mongo
from utils import entity_resolver


class ParseAppc:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.resolver = entity_resolver.MasterEntitiesResolver()
        self.PREFIX = "appc"
        if kwargs["refreshdb"]:
            self.db.drop("%s_parse" % self.PREFIX)

    def run(self):
        self._logger.debug("\n\nParsing APPC")
        all_entries = self.db.fetch_all("%s_scrape" % self.PREFIX, paged=False)
        for document in all_entries:
            name = self.resolver.map_lobby_agency(document["name"])
            self._logger.debug("\nLobbying Firm: %s" % name)

            clients = self._parse_clients(document["clients"])
            staff = self._parse_staff(document["staff"])
            countries = self._parse_countries(document["countries"])
            entry = {
                "name": name,
                "contact_details": self._collapse_list(document["contacts"]),
                "address": self._collapse_list(document["addresses"]),
                "pa_contact": self._fill_empty_field("pa_contact", document),
                "date_range": document["date_range"],
                "clients": clients,
                "staff": staff,
                "countries": countries,
                "source": document["source"]
            }
            self.db.save("%s_parse" % self.PREFIX, entry)

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
                self._logger.debug("~ %s" % self._normalize_text(entry))
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
    def _collapse_list(content):
        result = ["\n".join(x) for x in content]
        if len(result) > 1:
            result = "\n\n".join(result)
        else:
            result = result[0]
        return result

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


def parse(**kwargs):
    ParseAppc(**kwargs).run()