# -*- coding: utf-8 -*-
import calendar
from datetime import datetime
import os
import os.path
import logging
import re
import string
import time
import urllib
import requests
from bs4 import BeautifulSoup
from utils import mongo


class FetchAPPC:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.BASE_URL = "http://www.appc.org.uk"
        # database stuff
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "appc_fetch"
        if kwargs["refreshdb"]:
            self.db.drop(self.COLLECTION_NAME)
        # if True, avoid downloading where possible
        self.dryrun = kwargs["dryrun"]

    def run(self):
        self._logger.info("Fetching APPC")
        self.fetch_html_register()
        self.fetch_pdfs()

    def fetch_html_register(self):
        self._logger.info("Fetching APPC HTML ...")
        index_url = "%s/members/register/" % self.BASE_URL
        self._logger.debug("... %s" % index_url)
        r = requests.get(index_url)
        time.sleep(0.5)
        soup = BeautifulSoup(r.text)

        date_range = self.get_dates(soup.h1.text)

        rel_path = os.path.join(self.STORE_DIR, date_range[1])
        company_path = os.path.join(self.current_path, rel_path)
        if not os.path.exists(company_path):
            os.makedirs(company_path)

        companies = [x["value"] for x in soup.find_all("input", {"name": "company"})]
        for company in companies:
            fetched = False
            filename = os.path.join(rel_path, "%s.html" % self.filenamify(company))
            spec = {"filename": filename, "date_range": date_range}
            # Skip if we already have data for this company during this
            # date range in the database
            if self.db.find_one(self.COLLECTION_NAME, spec):
                self._logger.info("  Skipping '%s'" % company)
                continue

            if not self.dryrun:
                self.fetch_company(company, filename)
                fetched = str(datetime.now())

            meta = {
                "filename": filename,
                "date_range": date_range,
                "source": {
                    "url": None,  # unfortunately we don't have a direct link
                    "linked_from_url": index_url,
                    "fetched": fetched,
                }
            }

            self.db.save(self.COLLECTION_NAME, meta)
        self._logger.info("Done fetching APPC HTML.")

    def fetch_company(self, company, filename):
        self._logger.debug("  Fetching HTML for '%s' ..." % company)

        url = "%s/members/register/register-profile/" % self.BASE_URL
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.post(url, data={"company": company}, headers=headers)
        time.sleep(0.5)

        full_path = os.path.join(self.current_path, filename)
        with open(full_path, "w") as f:
            f.write(r.text.encode('utf-8'))
        return filename

    def fetch_pdfs(self):
        self._logger.info("Fetching APPC PDFs ...")
        pdf_index_url = "%s/previous-registers/" % self.BASE_URL
        rel_path = os.path.join(self.STORE_DIR, "archive")
        archive_path = os.path.join(self.current_path, rel_path)
        if not os.path.exists(archive_path):
            os.makedirs(archive_path)
        r = requests.get(pdf_index_url)
        time.sleep(0.5)
        soup = BeautifulSoup(r.text)
        paras = soup.find(class_="page").find_all("p")
        for p in paras:
            if not p.a:
                continue

            date_range = self.get_dates(p.text)

            # Skip if we already have data for this date range in the database
            if self.db.find_one(self.COLLECTION_NAME, {"date_range": date_range}):
                self._logger.info("  Skipping '%s'" % p.text)
                continue

            pdf_url = p.a["href"]
            filename = os.path.join(rel_path, pdf_url.split("/")[-1])
            full_path = os.path.join(self.current_path, filename)
            fetched = False

            if not self.dryrun:
                self._logger.debug("  Fetching PDF '%s' ..." % p.text)
                urllib.urlretrieve(pdf_url, full_path)
                fetched = str(datetime.now())
                time.sleep(0.5)

            meta = {
                "filename": filename,
                "date_range": date_range,
                "source": {
                    "url": pdf_url,
                    "linked_from_url": pdf_index_url,
                    "fetched": fetched,
                }
            }

            self.db.save(self.COLLECTION_NAME, meta)
        self._logger.info("Done fetching APPC PDFs.")

    # make a string filename-safe
    def filenamify(self, text):
        allowed_chars = "-_%s%s" % (string.ascii_letters, string.digits)
        return "".join(c if c in allowed_chars else "-" for c in text.lower())

    # parse out a pair of dates (with a known format) from a string
    # returns a tuple of dates in the form YYYY-MM-DD
    def get_dates(self, text):
        months = "|".join(calendar.month_name[1:])
        date_range = re.findall(r"(\d+).*?(%s) (\d{4})" % months, text)
        return [str(datetime.strptime(" ".join(i for i in x), "%d %B %Y").date()) for x in date_range]

def fetch(**kwargs):
    FetchAPPC(**kwargs).run()
