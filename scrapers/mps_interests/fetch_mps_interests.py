# -*- coding: utf-8 -*-
from datetime import datetime
import os.path
import logging
import requests
import time
import urllib
from bs4 import BeautifulSoup
from utils import mongo


class FetchMPsInterests:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        # path to submodule where historical regmem files are saved
        self.OLD_DATA_DIR = os.path.join("parldata", "scrapedxml", "regmem")
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        # regmem data is produced by the parlparse project which dumps
        # http://www.publications.parliament.uk/pa/cm/cmregmem/memi0910.htm
        # into an xml file. Each file stores interests as recorded on a
        # given day
        self.BASE_URL = "http://www.theyworkforyou.com/pwdata/scrapedxml/regmem/"
        self.LINKED_FROM_URL = "http://www.publications.parliament.uk/pa/cm/cmregmem.htm"
        # database stuff
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "mps_interests_fetch"
        if kwargs["refreshdb"]:
            self.db.drop(self.COLLECTION_NAME)
        # if True, avoid downloading where possible
        self.dryrun = kwargs["dryrun"]

    def run(self):
        self._logger.info("Adding old MPs interests XML to db ...")
        with open(os.path.join(self.current_path, self.OLD_DATA_DIR, "changedates.txt")) as f:
            prefetched = [x.strip().split(",") for x in f.readlines()]
            prefetched = {x[1]: x for x in prefetched}.values()

        for timestamp, filename in prefetched:
            date = filename[6:16]
            meta = {
                "filename": os.path.join(self.OLD_DATA_DIR, filename),
                "date": date,
                "source": {
                    "url": None,  # TODO: this is a bit tricky to discern
                    "linked_from_url": self.LINKED_FROM_URL,
                    "fetched": str(datetime.fromtimestamp(int(timestamp))),
                },
            }
            self.db.update(self.COLLECTION_NAME, {"date": date}, meta, upsert=True)
        self._logger.info("Done.")

        self._logger.info("Fetching MPs interests XML ...")
        r = requests.get(self.BASE_URL + "changedates.txt")
        to_fetch = [x.split(",") for x in r.text.split("\n") if x != ""]
        for timestamp, filename in to_fetch:
            date = filename[6:16]
            full_path = os.path.join(self.current_path, self.STORE_DIR, filename)

            if self.db.find_one(self.COLLECTION_NAME, {"date": date}):
                # we already have this, probably as part of the prefetched data
                continue

            if date == "2010-09-16":
                # this date is mysteriously in the parlparse changedates.txt
                # logfile, but the data is not on parliament.uk or on parlparse
                continue

            if not (os.path.exists(full_path) and self.dryrun):
                url = self.BASE_URL + filename
                self._logger.info("  Fetching %s ..." % url)
                urllib.urlretrieve(url, full_path)
                time.sleep(0.5)

            meta = {
                "filename": os.path.join(self.STORE_DIR, filename),
                "date": date,
                "source": {
                    "url": None,
                    "linked_from_url": self.LINKED_FROM_URL,
                    "fetched": str(datetime.fromtimestamp(int(timestamp))),
                },
            }
            self.db.save(self.COLLECTION_NAME, meta)
        self._logger.info("Done.")


def fetch(**kwargs):
    FetchMPsInterests(**kwargs).run()
