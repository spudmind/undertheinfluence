# -*- coding: utf-8 -*-
import logging
import os.path
import json
from utils import mongo


class ScrapeMPs:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        # database stuff
        self.db = mongo.MongoInterface()
        self.PREFIX = "mps"
        if kwargs["refreshdb"]:
            self.db.drop("%s_scrape" % self.PREFIX)

    def run(self):
        self._logger.info("Scraping MPs ...")
        metas = self.db.fetch_all("%s_fetch" % self.PREFIX, paged=False)
        for meta in metas:
            mp = self.get_mp_details(meta)
            self.db.save("%s_scrape" % self.PREFIX, mp)
        self._logger.info("Done scraping MPs.")

    def get_mp_details(self, meta):
        publicwhip_tmpl = u"http://publicwhip.com/mp.php?mpid={0}"
        with open(os.path.join(self.current_path, meta["filename"])) as f:
            mp = json.load(f)
        details = mp.pop("details")

        mp["twfy_id"] = details[0]["person_id"]
        # we set the party and member ID using the most recent
        # information
        mp["first_name"] = details[0]["first_name"]
        mp["last_name"] = details[0]["last_name"]
        mp["party"] = details[0]["party"]
        mp["publicwhip_id"] = details[0]["member_id"]
        mp["publicwhip_url"] = publicwhip_tmpl.format(mp["twfy_id"])

        mp["source"] = meta["source"]

        mp["aliases"] = []
        for x in details:
            full_name = "%s %s" % (x["first_name"], x["last_name"])
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

def scrape(**kwargs):
    ScrapeMPs(**kwargs).run()
