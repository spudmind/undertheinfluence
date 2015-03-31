s# -*- coding: utf-8 -*-
import logging
import os.path
import json
from utils import mongo


class ScrapeMPs:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "mps_scrape"
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        if kwargs["refreshdb"]:
            self.db.drop(self.COLLECTION_NAME)

    def run(self):
        self._logger.info("Importing MPs")
        mps = self.get_overview_data()
        for mp in mps:
            mp = self.get_mp_details(mp)
            self.db.save(self.COLLECTION_NAME, mp)

    def get_overview_data(self):
        publicwhip_tmpl = u"http://publicwhip.com/mp.php?mpid={0}"
        with open(os.path.join(self.current_path, self.STORE_DIR, "mps_overview.json")) as f:
            mps = json.load(f)
        data = []
        for mp in mps:
            self._print_out("MP", mp["name"])
            data.append({
                "full_name": mp["name"],
                "twfy_id": mp["person_id"],
                "party": mp["party"],
                "publicwhip_id": mp["member_id"],
                "publicwhip_url": publicwhip_tmpl.format(mp["person_id"]),
            })
            # self._logger.debug("\n")
        return data

    def get_mp_details(self, mp):
        with open(os.path.join(self.current_path, self.STORE_DIR, "%s.json" % mp["twfy_id"])) as f:
            info = json.load(f)
        details = info.pop("details")
        mp = dict(mp.items() + info.items())

        image = details[0].get("image")
        mp["first_name"] = details[0]["first_name"]
        mp["last_name"] = details[0]["last_name"]
        mp["image"] = "http://www.theyworkforyou.com%s" % image if image else None
        mp["number_of_terms"] = len(details)

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
        mp["terms"] = terms
        self._report(mp)
        return mp

    @staticmethod
    def _get_office(positions):
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
        self._logger.debug("\n\n---")

    def _print_out(self, key, value):
        self._logger.debug("  %-35s%-25s" % (key, value))


def scrape(**kwargs):
    ScrapeMPs(**kwargs).run()
