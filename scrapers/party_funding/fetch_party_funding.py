# -*- coding: utf-8 -*-
from datetime import datetime
import os.path
import logging
import time
import mechanize
from utils import mongo


class FetchPartyFunding:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.BASE_URL = "https://pefonline.electoralcommission.org.uk/Search/SearchIntro.aspx"
        # database stuff
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "party_funding_fetch"
        if kwargs["refreshdb"]:
            self.db.drop(self.COLLECTION_NAME)
        # if True, avoid downloading where possible
        self.dryrun = kwargs["dryrun"]

    def run(self):
        self._logger.info("Fetching Electoral Commission party funding data ...")
        # EC records start in 2001 (set to start collecting from 2005)
        year = 2005
        fetched = False
        while year <= datetime.now().year:
            filename = os.path.join(self.STORE_DIR, "ec-%s.csv" % year)
            if not self.dryrun:
                fetched = self.fetch(str(year), filename)
            meta = {
                "filename": filename,
                "year": year,
                "source": {
                    "url": None,  # unfortunately we don't have a direct link
                    "linked_from_url": self.BASE_URL,
                    "fetched": fetched,
                }
            }
            self.db.save(self.COLLECTION_NAME, meta)
            year += 1
        self._logger.info("Done fetching Electoral Commission party funding data.")

    def fetch(self, year, filename):
        br = mechanize.Browser()
        # load the search page
        _ = br.open(self.BASE_URL)
        time.sleep(0.5)
        br.select_form(name="aspnetForm")
        # click to view "Basic donation search"
        _ = br.submit(name="ctl00$ctl05$ctl01")
        time.sleep(0.5)
        br.select_form(name="aspnetForm")
        prefix = "ctl00$ContentPlaceHolder1$searchControl1$dtAccepted"
        # 1st Jan
        br.form[prefix + "From$ddlDay"] = ["1"]
        br.form[prefix + "From$ddlMonth"] = ["1"]
        # 31st Dec
        br.form[prefix + "To$ddlDay"] = ["31"]
        br.form[prefix + "To$ddlMonth"] = ["12"]

        br.form[prefix + "From$ddlYear"] = [year]
        br.form[prefix + "To$ddlYear"] = [year]

        # click to export results to CSV file
        csv_gen = br.submit(name="ctl00$ContentPlaceHolder1$searchControl1$btnExportAllResults")
        fetched = str(datetime.now())
        time.sleep(0.5)
        with open(os.path.join(self.current_path, filename), 'w') as f:
            for csv_line in csv_gen:
                f.write(csv_line)
        return fetched


def fetch(**kwargs):
    FetchPartyFunding(**kwargs).run()
