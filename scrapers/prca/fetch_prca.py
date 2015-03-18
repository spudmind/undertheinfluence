# -*- coding: utf-8 -*-
import logging
import calendar
from datetime import datetime
import os.path
import re
import time
import urllib
import requests
from bs4 import BeautifulSoup
from utils import mongo

"""
Fetch all the files at:
http://www.prca.org.uk/paregister
and store them.

A log of fetched files is also stored
in the database
"""


class FetchPRCA():
    def __init__(self):
        # fetch the logger
        self._logger = logging.getLogger("spud")
        # PRCA website
        self.BASE_URL = "http://www.prca.org.uk"
        self.index_url = "%s/paregister" % self.BASE_URL
        # shortcut to get a pipe-delimited string of all months
        MONTHS = "|".join(calendar.month_name[1:])
        self.DATE_RE = re.compile(r"(%s).*?(\d{4})" % MONTHS)
        # database stuff
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "prca_fetch"
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # the URL for this particular register is incorrect
        self.URL_CORRECTION = (("2012-12", "2013-02", "in-house"), "/assets/files/IN-HOUSE%20PRCA%20Public%20Affairs%20Register%20March%202013.pdf")
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))

    def scrape_index(self):
        self._logger.info("Fetching PRCA index page (%s) ..." % self.index_url)
        # fetch the index page
        r = requests.get(self.index_url)
        time.sleep(0.5)
        soup = BeautifulSoup(r.text)

        # get link and anchor text - working around links split in half
        links = [(li.text, link["href"]) for li in soup.find(id="content_1327").find_all("li") for link in li.find_all("a")]
        self._logger.info("... Index Scraped.")
        return links

    def parse_text(self, anchor_text):
        # fetch the start date...
        start = self.DATE_RE.search(anchor_text)
        start_dt = datetime.strptime("-".join(start.groups()), "%B-%Y")
        # ...and end date
        end = self.DATE_RE.search(anchor_text[start.start()+1:])
        end_dt = datetime.strptime("-".join(end.groups()), "%B-%Y")
        # set the day to the end of the month
        end_day = calendar.monthrange(end_dt.year, end_dt.month)[1]
        end_dt = end_dt.replace(day=end_day)
        # ensure start date is before end date!
        if start_dt > end_dt:
            # fixes e.g. "December to February 2013"
            start_dt = start_dt.replace(year=start_dt.year-1)

        if anchor_text.lower().find("agency") != -1:
            desc = "agency"
        elif re.search(r"in-?house", anchor_text, flags=re.IGNORECASE) is not None:
            desc = "in-house"
        else:
            desc = "mixed"

        return {"date_from": datetime.strftime(start_dt, "%Y-%m-%d"), "date_to": datetime.strftime(end_dt, "%Y-%m-%d"), "description": desc}

    def fetch_file(self, record):
        # name the file
        file_type = record["source"][-3:]
        filename = "%s_%s_%s.%s" % (record["description"], record["date_from"][:7], record["date_to"][:7], file_type)
        full_path = os.path.join(self.current_path, self.STORE_DIR, filename)
        # fetch from URL and save locally
        try:
            _ = urllib.urlretrieve(record["source"], full_path)
            time.sleep(0.5)
        except IOError:
            self._logger.error("URL not found: %s" % record["source"])
            raise
        # record filename and timestamp in the db
        record["filename"] = filename
        record["fetched"] = str(datetime.now())
        self._logger.info("... fetched %s." % filename)
        self.db.save(self.COLLECTION_NAME, record)

    def run(self):
        self._logger.info("Fetching PRCA")
        links = self.scrape_index()
        for anchor_text, rel_url in links:
            current = self.parse_text(anchor_text)

            # hack to fix broken URL in source
            if (current["date_from"][:7], current["date_to"][:7], current["description"]) == self.URL_CORRECTION[0]:
                rel_url = self.URL_CORRECTION[1]

            # fetch db instance matching this one
            existing = self.db.find_one(self.COLLECTION_NAME, current)
            if existing:
                # this is already in the db
                current = existing
                if current["fetched"]:
                    # this is already fetched too, so skip
                    continue
            else:
                # store a record in the db, but with fetched=False
                current["fetched"] = False
                current["source"] = "%s%s" % (self.BASE_URL, rel_url)
                current["linked_from"] = self.index_url
                self.db.save(self.COLLECTION_NAME, current)
            self.fetch_file(current)


def fetch():
    FetchPRCA().run()
