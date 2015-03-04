# -*- coding: utf-8 -*-
import os.path
import logging
import time
import json
from data_interfaces import hansard


class FetchMPs():
    def __init__(self):
        self._logger = logging.getLogger("spud")
        self.hansard = hansard.TWFYHansard()
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))

    def run(self):
        self._logger.info("Fetching MPs")
        mp_ids = self.get_overview_data()
        for mp_id in mp_ids:
            if os.path.exists(os.path.join(self.current_path, self.STORE_DIR, "%s.json" % mp_id)):
                continue
            self.get_mp_details(mp_id)
            time.sleep(0.5)

    def get_overview_data(self):
        self._logger.info("Fetching MP data from TheyWorkForYou")
        mps = self.hansard.get_mps()
        path = os.path.join(self.current_path, self.STORE_DIR, "mps_overview.json")
        with open(path, "w") as f:
            json.dump(mps, f)
        return [mp["person_id"] for mp in mps]

    def get_mp_details(self, mp_id):
        details = self.hansard.get_mp_details(mp_id)
        path = os.path.join(self.current_path, self.STORE_DIR, "%s.json" % mp_id)
        with open(path, "w") as f:
            json.dump(details, f)

def fetch():
    FetchMPs().run()
