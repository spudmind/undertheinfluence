# -*- coding: utf-8 -*-
from datetime import datetime
import os.path
import logging
import time
import json
from data_interfaces import hansard
from utils import mongo


class FetchLords:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger("spud")
        self.hansard = hansard.TWFYHansard()
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        # database stuff
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "lords_fetch"
        if kwargs["refreshdb"]:
            self.db.drop(self.COLLECTION_NAME)
        # if True, avoid downloading where possible
        self.dryrun = kwargs["dryrun"]

    def run(self):
        self._logger.info("Fetching current Lords data from TheyWorkForYou ...")
        lord_ids = self.get_overview_data()
        index_url = "http://www.theyworkforyou.com/api/docs/getLords?output=js#output"
        for lord_id in lord_ids:
            self.get_lord_details(lord_id, index_url)
        self._logger.info("Done fetching Lords.")

    def get_overview_data(self):
        lords = self.hansard.get_lords()
        time.sleep(0.5)

        if not self.dryrun:
            path = os.path.join(self.current_path, self.STORE_DIR, "overview.json")
            with open(path, "w") as f:
                json.dump(lords, f)

        return [lord["person_id"] for lord in lords]

    def get_lord_details(self, lord_id, index_url):
        filename = os.path.join(self.STORE_DIR, "%s.json" % lord_id)
        fetched = False

        if not self.dryrun:
            self._logger.info("  Fetching data for Lord with person ID '%s'" % lord_id)
            details = self.hansard.get_lord(lord_id)
            fetched = str(datetime.now())
            time.sleep(0.5)
            full_path = os.path.join(self.current_path, filename)
            with open(full_path, "w") as f:
                json.dump(details, f)

        meta = {
            "filename": filename,
            "source": {
                "url": "http://www.theyworkforyou.com/api/docs/getLord?id=%s&output=js#output" % lord_id,
                "linked_from_url": index_url,
                "fetched": fetched,
            }
        }
        self.db.update(self.COLLECTION_NAME, {"filename": filename}, meta, upsert=True)


def fetch(**kwargs):
    FetchLords(**kwargs).run()
