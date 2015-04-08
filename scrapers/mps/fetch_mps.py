# -*- coding: utf-8 -*-
import datetime
import os.path
import logging
import sets
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
        mp_ids = self.get_mps_since("2000-01-01", 180)
        self._logger.info("  Fetching individual MP data ...")
        for mp_id in mp_ids:
            self.get_mp_info(mp_id)
        self._logger.info("Done.")

    def get_mps_since(self, since, increment):
        all_mps = sets.Set()
        now = datetime.date.today()
        date = datetime.datetime.strptime(since, "%Y-%m-%d").date()
        while date < now:
            all_mps.update(self.get_overview_data(date=date))
            print "  MPs found so far: %s" % len(all_mps)
            date += datetime.timedelta(increment)
        all_mps.update(self.get_overview_data(date=now))
        return all_mps

    def get_overview_data(self, date):
        date_str = date.strftime("%d/%m/%Y")
        self._logger.info("  Fetching MP overview data from TheyWorkForYou (%s) ..." % date_str)

        path = os.path.join(self.current_path, self.STORE_DIR, "mps_overview_%s.json" % str(date))
        if os.path.exists(path) and self.dryrun:
            with open(path) as f:
                mps = json.load(f)
        else:
            mps = self.hansard.get_mps(date=date_str)
            time.sleep(0.5)
            with open(path, "w") as local:
                json.dump(mps, local)

        return [mp["person_id"] for mp in mps]

    def get_mp_info(self, mp_id):
        path = os.path.join(self.current_path, self.STORE_DIR, "%s.json" % mp_id)
        self._logger.debug("... %s" % path)
        if os.path.exists(path) and self.dryrun:
            # if the MP file exists, we bail out
            return

        extra_fields = ", ".join(["wikipedia_url", "bbc_profile_url", "date_of_birth", "mp_website", "guardian_mp_summary", "journa_list_link"])
        info = self.hansard.get_mp_info(mp_id, fields=extra_fields)
        time.sleep(0.5)

        info["details"] = self.hansard.get_mp(mp_id)
        time.sleep(0.5)

        with open(path, "w") as f:
            json.dump(info, f)


def fetch(**kwargs):
    FetchMPs(**kwargs).run()
