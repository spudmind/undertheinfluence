# -*- coding: utf-8 -*-
import logging
import os.path
import json
from utils import mongo


class ScrapeLords():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))

    def run(self):
        self._logger.info("Importing Lords")
        lords = self.get_overview_data()
        for lord in lords:
            lord = self.get_lord_details(lord)
            self.db.save("lords_scrape", lord)

    def get_overview_data(self):
        with open(os.path.join(self.current_path, self.STORE_DIR, "overview.json")) as f:
            lords = json.load(f)
        data = []
        for lord in lords:
            self._print_out("Lord", lord["name"])
            self._print_out("Party", lord["party"])
            self._print_out("person_id", lord["person_id"])
            data.append({
                "full_name": lord["name"],
                "twfy_id": lord["person_id"],
                "party": lord["party"],
            })
            # self._logger.debug("\n")
        return data

    def get_lord_details(self, lord):
        with open(os.path.join(self.current_path, self.STORE_DIR, "%s.json" % lord["twfy_id"])) as f:
            details = json.load(f)
        image = details[0].get("image")
        lord["first_name"] = details[0]["first_name"]
        lord["last_name"] = details[0]["last_name"]
        lord["title"] = details[0]["title"]
        lord["image"] = "http://www.theyworkforyou.com%s" % image if image else None
        lord["number_of_terms"] = len(details)
        self._print_out("first_name", lord["first_name"])
        self._print_out("last_name", lord["last_name"])

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
        lord["terms"] = terms
        #self._report(lord)
        return lord
        # self._logger.debug("\n\n---")

    def _update_cached_mp(self, id, key, value):
        self.cache_data.update({"_id": id}, {"$set": {key: value}})

    def _get_office(self, positions):
        offices = []
        for position in positions:
            office = {}
            if position["dept"]:
                office = {"department": position["dept"]}
            if position["position"]:
                office = {"position": position["position"]}
            offices.append(office)
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

def scrape():
    ScrapeLords().run()
