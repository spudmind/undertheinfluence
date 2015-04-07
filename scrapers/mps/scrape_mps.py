# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import os
import os.path
import json
import re
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
        self._logger.info("Scraping MPs ...")
        path = os.path.join(self.current_path, self.STORE_DIR)
        filenames = os.listdir(path)
        for filename in filenames:
            if not re.match(r"^\d+\.json$", filename):
                continue
            with open(os.path.join(path, filename)) as f:
                print os.path.join(path, filename)
                mp = json.load(f)
            mp = self.get_mp_details(mp)
            self.db.save(self.COLLECTION_NAME, mp)
        self._logger.info("Done scraping MPs.")

    def get_mp_details(self, mp):
        publicwhip_tmpl = u"http://publicwhip.com/mp.php?mpid={0}"
        details = mp["details"]
        mp = {x: mp.get(x, None) for x in ["wikipedia_url", "bbc_profile_url", "date_of_birth", "mp_website", "guardian_mp_summary", "journa_list_link"]}

        mp["full_name"] = u"{} {}".format(details[0]["first_name"], details[0]["last_name"])
        mp["twfy_id"] = details[0]["person_id"]
        mp["first_name"] = details[0]["first_name"]
        mp["last_name"] = details[0]["last_name"]
        # we set the party and member ID using the most recent information
        mp["party"] = details[0]["party"]
        mp["publicwhip_id"] = details[0]["member_id"]
        mp["publicwhip_url"] = publicwhip_tmpl.format(mp["twfy_id"])

        mp["source"] = {
            "url": "http://www.theyworkforyou.com/api/docs/getMP?id=%s&output=js#output" % mp["twfy_id"],
            "linked_from_url": None,
            "fetched": str(datetime.strptime(details[0]["lastupdate"], "%Y-%m-%d %H:%M:%S")),
        }

        mp["aliases"] = []
        for x in details:
            full_name = U"%s %s" % (x["first_name"], x["last_name"])
            if full_name not in mp["aliases"]:
                mp["aliases"].append(full_name)

        image = details[0].get("image")
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

    def _print_out(self, key, value):
        self._logger.debug("  %-35s%-25s" % (key, value))


def scrape(**kwargs):
    ScrapeMPs(**kwargs).run()
