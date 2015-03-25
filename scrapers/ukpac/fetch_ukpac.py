# -*- coding: utf-8 -*-
import os.path
import logging
import time
import requests
from bs4 import BeautifulSoup
from utils import mongo


class FetchUKPAC:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.BASE_URL = "http://www.publicaffairscouncil.org.uk"

    def run(self):
        self.fetch_company_urls()

    def fetch_company_urls(self):
        search_url = "%s/en/search-the-register/index.cfm/page/%d/search/SearchRegister/register/corporate/" % self.BASE_URL
        page = 1
        while True:
            r = requests.get(search_url % page)
            time.sleep(0.5)
            soup = BeautifulSoup(r.text)
            results = soup.find(class_="listing-filter-results")
            if not results:
                break
            dts = results.find_all("dt")
            company_urls = [(dt.a.text, dt.a["href"]) for dt in dts if dt.a]
            for company, url in company_urls:
                self.fetch_company(url)
            page += 1

    # this does the same thing as APPC, but it fetches from
    # UKPAC so we get a URL per company
    def fetch_company(self, url):
        r = requests.get(url)
        time.sleep(0.5)

        filename = "%s.html" % url.split("/")[-1]
        full_path = os.path.join(self.current_path, self.STORE_DIR, filename)
        with open(full_path, "w") as f:
            f.write(r.text.encode('utf-8'))

def fetch(**kwargs):
    FetchUKPAC(**kwargs).run()
