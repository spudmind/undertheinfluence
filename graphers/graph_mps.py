# -*- coding: utf-8 -*-
import logging
from utils import mongo
from data_models import government_models


class GraphMPs():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.data_models = government_models
        self.PREFIX = "mps"

    def run(self):
        all_mps = self.db.fetch_all("%s_parse" % self.PREFIX, paged=False)
        for doc in all_mps:
            self._import(doc)

    def _import(self, node):
        terms = node["terms"]
        mp = self.graph_mp(node)
        if terms:
            self.import_terms(mp, terms)
            mp.set_membership()

    def graph_mp(self, node):
        self._logger.debug("\n..................")
        self._logger.debug("%s x %s" % (node["full_name"], node["number_of_terms"]))
        self._logger.debug(node["party"])
        self._logger.debug("..................")

        return self._create_mp(node)

    def _create_mp(self, mp_details):
        new_mp = self.data_models.MemberOfParliament(
            mp_details["full_name"], get_properties=False
        )
        if not new_mp.exists:
            new_mp.create()

        source = mp_details["source"]
        del mp_details["_id"]
        del mp_details["terms"]
        del mp_details["source"]

        mp_details["source_url"] = source["url"]
        mp_details["source_linked_from"] = source["linked_from_url"]
        mp_details["source_fetched"] = source["fetched"]

        new_mp.set_mp_details(mp_details)
        new_mp.link_party(mp_details["party"])

        return new_mp

    def import_terms(self, mp, terms):
        for term in terms:
            self._logger.debug('%s %s' % (term["constituency"], term["party"]))
            self._logger.debug('%s to %s' % (term["entered_house"], term["left_house"]))
            self._logger.debug(term["left_reason"])
            new_term = self._create_term(term)
            mp.link_elected_term(new_term)
            if "offices_held" in term:
                self._create_offices(new_term, term["offices_held"])
            self._logger.debug("-")

    def _create_term(self, term):
        session = u"{0} {1} {2} to {3}".format(
            term["constituency"],
            term["party"],
            term["entered_house"],
            term["left_house"]
        )
        new_term = self.data_models.TermInParliament(session)
        new_constituency = self.data_models.Constituency(term['constituency'])
        new_term.create()
        new_constituency.create()
        term_details = {
            "party": term["party"],
            "constituency": term['constituency'],
            "left_house": term["left_house"],
            "entered_house": term["entered_house"],
            "left_reason": term["left_reason"],
            "type": "Elected"
        }
        new_term.set_term_details(properties=term_details)
        new_term.link_constituency(new_constituency)
        return new_term

    def _create_offices(self, term, offices):
        self._logger.debug("*")
        if len(offices) > 1 and offices != "none":
            for office in offices:
                if "department" in office and office["department"]:
                    self._create_office(
                        term, "committee", office["department"]
                    )
                if "position" in office and office["position"]:
                    self._create_office(
                        term, "position", office["position"]
                    )
        else:
            if not offices == "none":
                if "department" in offices[0] and offices[0]["department"]:
                    self._create_office(
                        term, "committee", offices[0]["department"]
                    )
                if "position" in offices[0] and offices[0]["position"]:
                    self._create_office(
                        term, "position", offices[0]["position"]
                    )

    def _create_office(self, term, create_as, office):
        self._logger.debug(office)
        new_office = None
        if create_as == "committee":
            new_office = self.data_models.GovernmentOffice(office)
            new_office.create()
            new_office.is_committee()
        elif create_as == "position":
            new_office = self.data_models.GovernmentOffice(office)
            new_office.create()
            new_office.is_position()
        if new_office.exists:
            term.link_position(new_office)

    def _print_out(self, key, value):
        self._logger.debug("  %-20s%-15s" % (key, value))
