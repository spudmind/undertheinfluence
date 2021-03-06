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
    def __init__(self, **kwargs):
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
        if kwargs["refreshdb"]:
            self.db.drop(self.COLLECTION_NAME)
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # the URL for this particular register is incorrect
        self.URL_CORRECTION = ((("2012-12-01", "2013-02-28"), "in-house"), "/assets/files/IN-HOUSE%20PRCA%20Public%20Affairs%20Register%20March%202013.pdf")
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        # if True, avoid downloading where possible
        self.dryrun = kwargs["dryrun"]

    def scrape_index(self):
        self._logger.info("Fetching PRCA index page (%s) ..." % self.index_url)
        # fetch the index page
        r = requests.get(self.index_url)
        time.sleep(0.5)
        soup = BeautifulSoup(r.text)

        # get link and anchor text - working around links split in half
        links = [(li.text, link["href"]) for li in soup.find(id="content_1327").find_all("li") for link in li.find_all("a")]
        self._logger.info("PRCA Index fetched.")
        return links

    def parse_text(self, anchor_text):
        # fetch the start date...
        start = self.DATE_RE.search(anchor_text)
        start_date = datetime.strptime("-".join(start.groups()), "%B-%Y").date()
        # ...and end date
        end = self.DATE_RE.search(anchor_text[start.start()+1:])
        end_date = datetime.strptime("-".join(end.groups()), "%B-%Y").date()
        # set the day to the end of the month
        end_day = calendar.monthrange(end_date.year, end_date.month)[1]
        end_date = end_date.replace(day=end_day)
        # ensure start date is before end date!
        if start_date > end_date:
            # fixes e.g. "December to February 2013"
            start_date = start_date.replace(year=start_date.year-1)
        date_range = (str(start_date), str(end_date))

        if anchor_text.lower().find("agency") != -1:
            desc = "agency"
        elif re.search(r"in-?house", anchor_text, flags=re.IGNORECASE) is not None:
            desc = "in-house"
        else:
            desc = "mixed"

        return {"date_range": date_range, "description": desc}

    def fetch_file(self, record):
        # name the file
        full_path = os.path.join(self.current_path, self.STORE_DIR, record["filename"])
        # fetch from URL and save locally
        try:
            self._logger.info("Fetching '%s' ..." % full_path)
            _ = urllib.urlretrieve(record["source"]["url"], full_path)
            record["source"]["fetched"] = str(datetime.now())
            time.sleep(0.5)
        except IOError:
            self._logger.error("URL not found: %s" % record["source"]["url"])
            raise

        return record

    def run(self):
        self._logger.info("Fetching PRCA")
        links = self.scrape_index()
        for anchor_text, rel_url in links:
            current = self.parse_text(anchor_text)

            # hack to fix incorrect URL in source
            if (current["date_range"], current["description"]) == self.URL_CORRECTION[0]:
                rel_url = self.URL_CORRECTION[1]

            file_type = rel_url[-3:]
            filename = "%s_%s_%s.%s" % (
                current["description"],
                current["date_range"][0][:7],
                current["date_range"][1][:7],
                file_type
            )
            current["filename"] = filename

            if self.db.find_one(self.COLLECTION_NAME, current):
                self._logger.info("Skipping '%s' ..." % rel_url)
                continue

            current["source"] = {
                "url": "%s%s" % (self.BASE_URL, rel_url),
                "linked_from_url": self.index_url,
                "fetched": False,
            }

            if not self.dryrun:
                current = self.fetch_file(current)

            self.db.save(self.COLLECTION_NAME, current)


def fetch(**kwargs):
    FetchPRCA(**kwargs).run()
