# -*- coding: utf-8 -*-
from data_interfaces import hansard
from utils import mongo
import requests
import os
import logging


class LordsInfoScraper():
    current_path = os.path.dirname(os.path.abspath(__file__))
    ALL_PARTIES_API = 'http://www.theguardian.com/politics/api/party/all/json'
    VOTE_MATRIX = current_path + '/data/votematrix-2010.csv'
    TEST = None

    def __init__(self):
        self._logger = logging.getLogger('spud')

    def run(self):
        self._logger.info("Importing Lords")
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.scraped_lords_info
        self.requests = requests
        self.hansard = hansard.TWFYHansard()
        self.lords = self.hansard.get_lords()
        self.all_lords = None

        self._get_twfy_data()

    def _get_twfy_data(self):
        self._logger.info("Getting Lords from TWFY")
        for lord in self.lords:
            self._print_out("Lord", lord["name"])
            self._print_out("Party", lord["party"])
            self._print_out("person_id", lord["person_id"])
            node = {
                "full_name": lord["name"],
                "twfy_id": lord["person_id"],
                "publicwhip_id": None,
                "party": lord["party"],
                "guardian_url": None,
                "publicwhip_url": None,
                "guardian_image": None
            }
            # self._logger.debug("\n")
            details = self.hansard.get_lord_details(lord["person_id"])
            if details:
                node["first_name"] = details[0]["first_name"]
                node["last_name"] = details[0]["last_name"]
                node["title"] = details[0]["title"]
                node["number_of_terms"] = len(details)
                self._print_out("first_name", node["first_name"])
                self._print_out("last_name", node["last_name"])
            terms = []
            for entry in details:
                term = {
                    "party": entry["party"],
                    "constituency": entry['constituency'],
                    "left_house": entry["left_house"],
                    "entered_house": entry["entered_house"],
                    "left_reason": entry["left_reason"]
                }
                if "office" in entry:
                    offices = self._get_office(entry["office"])
                    if len(offices) > 0:
                        term["offices_held"] = offices
                terms.append(term)
            node["terms"] = terms
            #self._report(node)
            self.cache_data.save(node)
            # self._logger.debug("\n\n---")

    def _update_cached_mp(self, id, key, value):
        self.cache_data.update({"_id": id}, {"$set": {key: value}})

    def _get_office(self, positions):
        offices = []
        if len(positions) > 1:
            for position in positions:
                office = {}
                if position["dept"]:
                    office = {"department": position["dept"]}
                if position["position"]:
                    office = {"position": position["position"]}
                offices.append(office)
        else:
            office = {}
            if positions[0]["dept"]:
                office = {"department": positions[0]["dept"]}
            if positions[0]["position"]:
                office = {"position": positions[0]["position"]}
            offices.append(office)
        if len(offices) == 0:
            return None
        else:
            return offices

    def _report(self, node):
        for x in node:
                if x == "terms":
                    for term in node["terms"]:
                        self._logger.debug("-")
                        for y in term:
                            if y == "offices_held":
                                offices = term["offices_held"]
                                if len(offices) > 1 and offices != "none":
                                    for office in offices:
                                        for z in office:
                                            self._print_out(z, office[z])
                                else:
                                    if not offices == "none":
                                        for z in offices[0]:
                                            self._print_out(z, offices[0][z])
                            else:
                                self._print_out(y, term[y])
                else:
                    self._print_out(x, node[x])

    def _print_out(self, key, value):
        self._logger.debug("  %-35s%-25s" % (key, value))
