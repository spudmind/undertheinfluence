# -*- coding: utf-8 -*-
import logging

from utils import mongo
from utils import config
from utils import entity_resolver


class ParsePartyFunding():
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.resolver = entity_resolver.MasterEntitiesResolver()
        self.PREFIX = "party_funding"
        self.lords_titles = config.lords_titles
        if kwargs["refreshdb"]:
            self.db.drop("%s_parse" % self.PREFIX)

    def run(self):
        _all_entries = self.db.fetch_all("%s_scrape" % self.PREFIX, paged=False)
        for doc in _all_entries:
            parsed = {}
            # skip the header row
            if not doc["ec_reference"].lower() == "ec reference":
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
                parsed["source"] = doc["source"]
                if not parsed["recipient"]:
                    self._print_dic(parsed)
                    self._logger.debug("---\n")
                else:
                    self._print_out("recipient", doc["recipient"])
                    self._print_out("found", parsed["recipient"])
                    self._print_out("donee_type", parsed["donee_type"])
                    self._print_out("donor_name", doc["donor_name"])
                    self._print_out("found_name", parsed["donor_name"])
                    self._print_out("donor_type", parsed["donor_type"])
                    #self._print_out("value", parsed["value"])
                    self._logger.debug("---\n")
                    self.db.save("%s_parse" % self.PREFIX, parsed)

    def _get_recipient(self, candidate, entry_type, recipient_type):
        # TODO Verify entity extraction is working as expected
        found = None
        clean = self._remove_extraneous(candidate)
        if self._is_party(candidate, entry_type, recipient_type):
            found = self.resolver.find_party(clean)
        else:
            if self._is_mp(candidate, entry_type, recipient_type):
                found = self.resolver.find_mp(clean)
            elif self._is_lord(candidate):
                found = self.resolver.find_lord(clean)
        if not found:
            found = self.resolver.get_entities(clean)
        return candidate if found is None else found

    def _get_donor(self, entry, entry_type):
        result = self._remove_extraneous(entry)
        if entry_type == "Individual":
            if self._is_lord(entry):
                result = self.resolver.find_lord(result)
            else:
                result = self.resolver.get_entities(result)
        else:
            result = self.resolver.find_influencer(
                entry, delimiter=",", fuzzy_delimit=False
            )
        if result and isinstance(result, list):
            result = result[0]
        if not result:
            return entry
        else:
            return result

    @staticmethod
    def _is_party(candidate, entry_type, recipient_type):
        found = False
        fields = [candidate, entry_type, recipient_type]
        search = ["Political Party", "Party"]
        for field in fields:
            if any(party_search in field for party_search in search):
                if "Third" not in field:
                    found = True
        return found

    @staticmethod
    def _is_mp(candidate, entry_type, recipient_type):
        found = False
        fields = [candidate, entry_type, recipient_type]
        search = ["Member of Parliament", "MP"]
        for field in fields:
            if any(mp_search in field for mp_search in search):
                found = True
        return found

    def _is_lord(self, candidate):
        found = False
        if any(title in candidate for title in self.lords_titles):
            found = True
        return found

    @staticmethod
    def _remove_broken_pound(text):
        return text.replace(u"��", u"£")

    @staticmethod
    def _remove_extraneous(text):
        text = text.replace("\\", " ")
        text = text.replace('"', ' ')
        return text

    def _print_out(self, key, value):
        self._logger.debug("  %-30s%-20s" % (key, value))

    def _print_dic(self, dictionary):
        for keys, values in dictionary.items():
            self._logger.debug(" %-20s:%-25s" % (keys, values))


def parse(**kwargs):
    ParsePartyFunding(**kwargs).run()