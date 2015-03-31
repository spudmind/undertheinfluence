# -*- coding: utf-8 -*-
import logging
import os.path
import json
from utils import mongo


class ScrapeLords:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "lords_scrape"
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        if kwargs["refreshdb"]:
            self.db.drop(self.COLLECTION_NAME)

    def run(self):
        self._logger.info("Importing Lords ...")
        lords = self.get_overview_data()
        for lord in lords:
            lord = self.get_lord_details(lord)
            self.db.save(self.COLLECTION_NAME, lord)
        self._logger.info("Done importing Lords.")

    def get_overview_data(self):
        publicwhip_tmpl = u"http://publicwhip.com/mp.php?mpid={0}"
        with open(os.path.join(self.current_path, self.STORE_DIR, "lords_overview.json")) as f:
            lords = json.load(f)
        data = []
        for lord in lords:
            self._print_out("Lord", lord["name"])
            data.append({
                "full_name": lord["name"],
                "twfy_id": lord["person_id"],
                "party": lord["party"],
                "publicwhip_id": lord["member_id"],
                "publicwhip_url": publicwhip_tmpl.format(lord["member_id"]),
            })

        return data

    def get_lord_details(self, meta):
        with open(os.path.join(self.current_path, self.STORE_DIR, "%s.json" % meta["twfy_id"])) as f:
            details = json.load(f)

        image = details[0].get("image")
        lord = {
            "title": details[0]["title"],
            # NB Lords' names appear to be broken in TWFY...
            "first_name": details[0]["first_name"],
            "last_name": details[0]["last_name"],
            "full_name": [details[0]["full_name"]],
            "party": details[0]["party"],
            "twfy_id": details[0]["person_id"],
            "image": "http://www.theyworkforyou.com%s" % image if image else None,
            "terms": [{
                "entered_house": term["entered_house"],
                "left_house": term["left_house"] if term['left_house'] != "9999-12-31" else None,
                "left_reason": term["left_reason"] if term['left_reason'] != "" else None,
                "constituency": term['constituency'] if term['constituency'] != "" else None,
                "party": term["party"],
            } for term in details],
            "source": meta["source"],
        }

        self._logger.debug(lord["name"])
        self._logger.debug(lord["party"])
        self._logger.debug("\n---")
        return lord

    def _print_out(self, key, value):
        self._logger.debug("  %-35s%-25s" % (key, value))


def scrape(**kwargs):
    ScrapeLords(**kwargs).run()
