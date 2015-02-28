# -*- coding: utf-8 -*-
import logging

from utils import mongo
from utils import config
from utils import entity_resolver


class PartyFundingParser():
    def __init__(self):
        self._logger = logging.getLogger('spud')

    def run(self):
        self.db = mongo.MongoInterface()
        self.resolver = entity_resolver.MasterEntitiesResolver()
        self.lords_titles = config.lords_titles

        _all_entries = self.db.fetch_all('scraped_party_funding', paged=False)
        for doc in _all_entries:
            parsed = {}
            parsed["recipient"] = self._get_recipient(
                doc["recipient"], doc["donee_type"], doc["recipient_type"]
            )
            parsed["donor_name"] = self._get_donor(
                doc["donor_name"], doc["donor_type"]
            )
            parsed["donor_type"] = doc["donor_type"]
            parsed["donee_type"] = doc["donee_type"]
            parsed["recipient_type"] = doc["recipient_type"]
            parsed["donation_type"] = doc["donation_type"]
            parsed["value"] = self._remove_broken_pound(doc["value"])
            parsed["purpose"] = doc["purpose"]
            parsed["nature_provision"] = doc["nature_provision"]
            parsed["ec_reference"] = doc["ec_reference"]
            parsed["company_reg"] = doc["company_reg"]
            parsed["is_sponsorship"] = doc["is_sponsorship"]
            parsed["6212"] = doc["6212"]
            parsed["recd_by"] = doc["recd_by"]
            parsed["received_date"] = doc["received_date"]
            parsed["reported_date"] = doc["reported_date"]
            parsed["accepted_date"] = doc["accepted_date"]
            if not parsed["recipient"]:
                self._print_dic(parsed)
                self._logger.debug("---\n")
            else:
                self._print_out("recipient", parsed["recipient"])
                self._print_out("donee_type", parsed["donee_type"])
                self._print_out("donor_name", doc["donor_name"])
                self._print_out("found_name", parsed["donor_name"])
                self._print_out("donor_type", parsed["donor_type"])
                self._print_out("value", parsed["value"])
                self._logger.debug("---\n")
                self.db.save('parsed_party_funding', parsed)

    def _get_recipient(self, entry, entry_type, recipient_type):
        result = self._remove_illegal_chars(entry)
        if entry_type == "MP - Member of Parliament":
            result = self.resolver.find_mp(result)
        elif entry_type == "Political Party" or \
                recipient_type == "Political Party":
            result = self.resolver.find_party(result)
        else:
            result = self.resolver.get_entities(result)
            if result and isinstance(result, list):
                result = result[0]
        if not result:
            return entry
        else:
            return result

    def _get_donor(self, entry, entry_type):
        result = self._remove_illegal_chars(entry)
        if entry_type == "Individual":
            title = entry.split(" ")[0]
            if title in self.lords_titles:
                result = self.resolver.find_lord(result)
            else:
                result = self.resolver.get_entities(result)
        else:
            result = self.resolver.find_donor(
                entry, delimiter=",", fuzzy_delimit=False
            )
        if result and isinstance(result, list):
            result = result[0]
        if not result:
            return entry
        else:
            return result

    @staticmethod
    def _remove_broken_pound(text):
        return text.replace(u"��", u"£")

    @staticmethod
    def _remove_illegal_chars(text):
        text = text.replace("\\", " ")
        return text

    def _print_out(self, key, value):
        self._logger.debug("  %-30s%-20s" % (key, value))

    def _print_dic(self, dictionary):
        for keys, values in dictionary.items():
            self._logger.debug(" %-20s:%-25s" % (keys, values))
