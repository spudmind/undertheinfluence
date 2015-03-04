# -*- coding: utf-8 -*-
import os.path
import logging
import time
import json
from data_interfaces import hansard

class FetchLords():
    def __init__(self):
        self._logger = logging.getLogger("spud")
        self.hansard = hansard.TWFYHansard()
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))

    def run(self):
        self._logger.info("Fetching Lords")
        lord_ids = self.get_overview_data()
        for lord_id in lord_ids:
            if os.path.exists(os.path.join(self.current_path, self.STORE_DIR, "%s.json" % lord_id)):
                continue
            self.get_lord_details(lord_id)
            time.sleep(0.5)

    def get_overview_data(self):
        self._logger.info("Fetching Lords data from TheyWorkForYou")
        lords = self.hansard.get_lords()
        path = os.path.join(self.current_path, self.STORE_DIR, "overview.json")
        with open(path, "w") as f:
            json.dump(lords, f)
        return [lord["person_id"] for lord in lords]

    def get_lord_details(self, lord_id):
        details = self.hansard.get_lord_details(lord_id)
        path = os.path.join(self.current_path, self.STORE_DIR, "%s.json" % lord_id)
        with open(path, "w") as f:
            json.dump(details, f)

def fetch():
    FetchLords().run()
