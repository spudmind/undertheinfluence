# -*- coding: utf-8 -*-
import datetime
import logging
import requests
import os.path
import time
from utils import mongo


class FetchLordsInterests:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.TMPL_URL = "http://data.parliament.uk/membersdataplatform/services/mnis/members/query/joinedbetween=%sand%s|lordsmemberbetween=%sand%s/Interests%%7CPreferredNames/"
        # arbitrarily start from 1st January 1940
        self.START_DATE = datetime.date(1940, 1, 1)
        # database stuff
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "lords_interests_fetch"
        if kwargs["refreshdb"]:
            self.db.drop(self.COLLECTION_NAME)
        # if True, avoid downloading where possible
        self.dryrun = kwargs["dryrun"]

    def run(self):
        self._logger.info("Fetching Lords interests JSON ...")
        headers = {"content-type": "application/json"}
        fetched = False
        today = datetime.date.today()
        start = self.START_DATE
        while start < today:
            end = start.replace(year=start.year + 5)
            date_range = (str(start), str(end))
            year_range = (start.year, end.year)

            # if end < today and self.db.find_one(self.COLLECTION_NAME, {"date_range": date_range}):
            #     self._logger.info("  Skipping %s-%s" % year_range)
            #     start = end
            #     continue

            filename = os.path.join(self.STORE_DIR, "%s-%s.json" % year_range)
            url = self.TMPL_URL % (date_range + date_range)
            if not self.dryrun:
                self._logger.info("  Fetching JSON for %s-%s ..." % year_range)
                r = requests.get(url, headers=headers)
                fetched = datetime.datetime.now()
                time.sleep(0.5)
                full_path = os.path.join(self.current_path, filename)
                with open(full_path, "w") as f:
                    f.write(r.text.encode("utf-8"))

            meta = {
                "filename": filename,
                "date_range": date_range,
                "source": {
                    "url": url,
                    "linked_from_url": None,
                    "fetched": fetched,
                }
            }
            self.db.update(self.COLLECTION_NAME, {"date_range": date_range}, meta, upsert=True)
            start = end
        self._logger.info("Done fetching Lords interests JSON.")

def fetch(**kwargs):
    FetchLordsInterests(**kwargs).run()
