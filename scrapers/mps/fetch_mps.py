# -*- coding: utf-8 -*-
from datetime import datetime
import os.path
import logging
import time
import json
from data_interfaces import hansard
from utils import mongo


class FetchMPs:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger("spud")
        self.hansard = hansard.TWFYHansard()
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        # database stuff
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "mps_fetch"
        if kwargs["refreshdb"]:
            self.db.drop(self.COLLECTION_NAME)
        # if True, avoid downloading where possible
        self.dryrun = kwargs["dryrun"]

    def run(self):
        self._logger.info("Fetching MPs ...")
        mp_ids = self.get_overview_data()
        self._logger.info("  Fetching individual MP data ...")
        for mp_id in mp_ids:
            self.get_mp_info(mp_id)
        self._logger.info("Done.")

    def get_overview_data(self, date="01/01/2015"):
        self._logger.info("  Fetching MP overview data from TheyWorkForYou ...")
        mps = self.hansard.get_mps(date=date)
        time.sleep(0.5)
        path = os.path.join(self.current_path, self.STORE_DIR, "mps_overview.json")
        with open(path, "w") as f:
            json.dump(mps, f)
        return [mp["person_id"] for mp in mps]

    def get_mp_info(self, mp_id):
        fetched = False
        filename = os.path.join(self.STORE_DIR, "%s.json" % mp_id)

        if not self.dryrun:
            extra_fields = ", ".join(["wikipedia_url", "bbc_profile_url", "date_of_birth", "mp_website", "guardian_mp_summary", "journa_list_link"])
            info = self.hansard.get_mp_info(mp_id, fields=extra_fields)
            time.sleep(0.5)

            info["details"] = self.hansard.get_mp_details(mp_id)
            fetched = str(datetime.now())
            time.sleep(0.5)

            path = os.path.join(self.current_path, filename)
            with open(path, "w") as f:
                json.dump(info, f)

        meta = {
            "filename": filename,
            "source": {
                "url": "http://www.theyworkforyou.com/api/docs/getMP?id=%s#output" % mp_id,
                "linked_from_url": None,
                "fetched": fetched,
            }
        }
        self.db.save(self.COLLECTION_NAME, meta)

def fetch(**kwargs):
    FetchMPs(**kwargs).run()
