# -*- coding: utf-8 -*-
import logging
from utils import mongo
from data_models import government_models


class GraphLords():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.data_models = government_models
        self.PREFIX = "lords"

    def run(self):
        all_lords = self.db.fetch_all("%s_parse" % self.PREFIX, paged=False)
        for doc in all_lords:
            self._import(doc)

    def _import(self, node):
        terms = node["terms"]
        lord = self.graph_lord(node)
        if terms:
            self.import_terms(lord, terms)

    def graph_lord(self, node):
        self._logger.debug("\n..................")
        self._logger.debug("%s x %s" % (node["full_name"], node["number_of_terms"]))
        if "also_known_as" in node:
            self._logger.debug("AKA: %s" % node["full_name"])
        self._logger.debug(node["party"])
        self._logger.debug("..................")
        # self._logger.debug(node["twfy_id"])
        return self._create_lord(node)

    def _create_lord(self, lord_details):
        new_lord = self.data_models.Lord(lord_details["full_name"])
        if not new_lord.exists:
            new_lord.create()

        source = lord_details["source"]
        del lord_details["_id"]
        del lord_details["terms"]
        del lord_details["source"]

        lord_details["source_url"] = source
        lord_details["source_linked_from"] = "http://www.theyworkforyou.com/api"
        lord_details["source_fetched"] = None

        new_lord.set_lord_details(lord_details)
        new_lord.link_party(lord_details["party"])

        return new_lord

    def import_terms(self, lord, terms):
        for term in terms:
            new_term = self._create_term(term)
            lord.link_peerage(new_term)
            self._logger.debug("-")

    def _create_term(self, term):
        session = u"{0} {1} {2} to {3}".format(
            term["constituency"],
            term["party"],
            term["entered_house"],
            term["left_house"]
        )
        new_term = self.data_models.TermInParliament(session)
        if not new_term.exists:
            new_term.create()
        label = "Peerage"
        term = {
            "party": term["party"],
            "constituency": term['constituency'],
            "left_house": term["left_house"],
            "entered_house": term["entered_house"],
            "left_reason": term["left_reason"],
            "type": "Peerage",
        }
        new_term.set_term_details(labels=label, properties=term)
        if term['constituency']:
            # self._logger.debug("--> %s" % term['constituency'])
            new_constituency = self.data_models.Constituency(term['constituency'])
            new_constituency.create()
            new_term.link_constituency(new_constituency)
        return new_term

    def _print_out(self, key, value):
        self._logger.debug("  %-20s%-15s" % (key, value))
