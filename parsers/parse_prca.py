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
        self._logger.debug("\n\nParsing PRCA")
        all_entries = self.db.fetch_all('prca_scrape', paged=False)

        for document in all_entries:
            clients = []
            staff = []
            name = self._normalize_text(document["name"])
            self._logger.debug("\nLobbying Firm: %s" % name)
            meta = document["meta"]
            meta["date_range"] = {
                "to": document["date_to"],
                "from": document["date_from"]
            }
            if "clients" in document:
                clients = self._parse_clients(document["clients"])
            if "staff" in document:
                staff = self._parse_staff(document["staff"])
            entry = {
                "lobbyist": {
                    "name": name,
                    "contact_details": " ".join(document["contact"]),
                    "pa_contact": self._fill_empty_field("pa_contact", document)
                },
                "clients": clients,
                "staff": staff,
                "meta": document["meta"]
            }
            #self.db.save("prca_parse", entry)

    def _parse_clients(self, clients):
        self._logger.debug("... Parsing Clients")
        client_list = []
        raw_clients = self._fix_list(clients)
        for entry in raw_clients:
            if self._has_data(entry):
                if self._unclosed_blacket(entry, "left"):
                    text = entry.split("(")
                    group_name = text[0].strip()
                    client_list.append(group_name)
                    self._logger.debug("# %s" % group_name)
                    client_list = client_list + self._parse_list(text[1].split(","))
                elif self._unclosed_blacket(entry, "right"):
                    if "," in entry:
                        client_list = client_list + self._parse_list(entry.split(","))
                    else:
                        text = self._normalize_text(entry, capitalize=False)
                        client_list.append(text)
                elif entry.count(",") > 1:
                    client_list = client_list + self._parse_list(entry.split(","))
                else:
                    entry = self._normalize_text(entry, capitalize=False)
                    client_list.append(entry)
                    self._logger.debug("* %s" % entry)
            else:
                self._logger.debug(">>>>> no data: %s" % entry)
        return [x for x in client_list if len(x) > 1]

    def _parse_staff(self, staff):
        self._logger.debug("... Parsing Staff")
        staff_list = []
        for entry in staff:
            if self._has_data(entry):
                if "," in entry:
                    entry = entry.split(",")[0]
                name = self._normalize_text(entry)
                staff_list.append(name)
                self._logger.debug("~ %s" % name)
            else:
                self._logger.debug(">>>>> no data: %s" % entry)
        return [x for x in staff_list if len(x) > 1]

    def _parse_list(self, entries):
        new_list = []
        for entry in entries:
            if len(entry) > 2:
                entry = self._normalize_text(entry, capitalize=False)
                new_list.append(entry)
                self._logger.debug("** %s" % entry)
        return new_list

    def _fix_list(self, raw_list):
        new_list = []
        broken_lines = [
            "Group", "Association", "Ltd", "Council", "Foundation", "Limited", "Society"
        ]
        for i, entry in enumerate(raw_list):
            broken = False
            new_entry = None
            for broken_line in broken_lines:
                if entry == broken_line or entry == u" {}".format(broken_line):
                    broken = True
                    new_entry = u"{0} {1}".format(raw_list[i-1].strip(), entry.strip())
            if broken:
                new_list.remove(raw_list[i-1])
                new_list.append(new_entry)
                self._logger.debug("! %s + %s" % (raw_list[i-1], entry))
            else:
                new_list.append(entry)
        return [x for x in new_list if x not in broken_lines]

    def _normalize_text(self, text, capitalize=True):
        text = self._strip_parentheses(text)
        if self._unclosed_blacket(text, "right"):
            text = text.strip(")")
        if "funded by: " in text:
            text = text.strip("funded by: ")
        if capitalize:
            if text.isupper():
                text = text.title()
        if len(text) > 1:
            if text[1] == "-":
                text = text.lstrip("-")
            if text[:2] == "- ":
                text = text.lstrip("-")
        return text.strip()

    def _has_data(self, text):
        result = True
        checks = [
            "Address:", "Website:", "Email:", "www.", "Telephone:",
            "@", "http:", "Employer:", "Employer:", "Job Title:",
            "comprising:", "Variable", u"", "N/A"
        ]
        clean_text = self._strip_parentheses(text)
        for test in checks:
            if test in clean_text:
                result = False
        if len(text) < 3 and text != "BT":
            result = False
        return result

    @staticmethod
    def _fill_empty_field(field, document):
        return None if field not in document else document[field]

    @staticmethod
    def _strip_parentheses(text):
        return re.sub('\(.+?\)\s*', '', text)

    @staticmethod
    def _unclosed_blacket(text, side=None):
        result = False
        if side == "left":
            if "(" in text and ")" not in text:
                result = True
        if side == "right":
            if ")" in text and "(" not in text:
                result = True
        return result



