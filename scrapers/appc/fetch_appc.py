# -*- coding: utf-8 -*-
import calendar
from datetime import datetime
import os.path
import logging
import re
import string
import time
import urllib
import requests
from bs4 import BeautifulSoup
<<<<<<< HEAD
from utils import mongo
=======
from utils import mongo, fuzzy_dates
>>>>>>> 59-prca-parse


class FetchAPPC:
    def __init__(self):
        self._logger = logging.getLogger('spud')
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.BASE_URL = "http://www.appc.org.uk"
<<<<<<< HEAD
        # database stuff
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "appc_fetch"
=======
>>>>>>> 59-prca-parse

    def run(self):
        self.fetch_html_register()
        self.fetch_pdfs()

    def fetch_html_register(self):
        index_url = "%s/members/register/" % self.BASE_URL
        r = requests.get(index_url)
        time.sleep(0.5)
        soup = BeautifulSoup(r.text)
<<<<<<< HEAD

        date_from, date_to = self.get_dates(soup.h1.text)

        companies = soup.find_all("input", {"name": "company"})
        for company in companies:
            filename = self.fetch_company(company["value"], date_to)
            meta = {
                "date_from": date_from,
                "date_to": date_to,
                "description": "current",
                "fetched": str(datetime.now()),
                "filename": filename,
                "linked_from": index_url,
                "source": None,
            }
            self.db.save(self.COLLECTION_NAME, meta)

    def fetch_company(self, company, date_to):
        url = "%s/members/register/register-profile/" % self.BASE_URL
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.post(url, data={"company": company}, headers=headers)
        time.sleep(0.5)

        filename = "%s.html" % self.filenamify(company)
        company_path = os.path.join(self.current_path, self.STORE_DIR, date_to)
=======
        date_range = self.get_dates(soup.h1.text)
        companies = soup.find_all("input", {"name": "company"})
        for company in companies:
            self.fetch_company(company["value"], date_range)

    def fetch_company(self, company, date_range):
        url = "%s/members/register/register-profile/" % self.BASE_URL
        r = requests.post(url, data={"company": company})
        time.sleep(0.5)

        filename = "%s.html" % self.filenamify(company)
        company_path = os.path.join(self.current_path, self.STORE_DIR, date_range[1])
>>>>>>> 59-prca-parse
        if not os.path.exists(company_path):
            os.makedirs(company_path)
        full_path = os.path.join(company_path, filename)
        with open(full_path, "w") as f:
            f.write(r.text.encode('utf-8'))
<<<<<<< HEAD
        return filename

    def fetch_pdfs(self):
        desc = "archive"
        pdf_index_url = "%s/previous-registers/" % self.BASE_URL
        archive_path = os.path.join(self.current_path, self.STORE_DIR, desc)
=======

    def fetch_pdfs(self):
        pdf_index_url = "%s/previous-registers/" % self.BASE_URL
        archive_path = os.path.join(self.current_path, self.STORE_DIR, "archive")
>>>>>>> 59-prca-parse
        if not os.path.exists(archive_path):
            os.makedirs(archive_path)
        r = requests.get(pdf_index_url)
        time.sleep(0.5)
        soup = BeautifulSoup(r.text)
        paras = soup.find(class_="page").find_all("p")
        for p in paras:
            if not p.a:
                continue
<<<<<<< HEAD
            date_from, date_to = self.get_dates(p.text)
            pdf_url = p.a["href"]
            filename = pdf_url.split("/")[-1]
            full_path = os.path.join(archive_path, filename)
            urllib.urlretrieve(pdf_url, full_path)
            time.sleep(0.5)

            meta = {
                "date_from": date_from,
                "date_to": date_to,
                "description": desc,
                "fetched": str(datetime.now()),
                "filename": filename,
                "linked_from": pdf_index_url,
                "source": pdf_url,
            }
            self.db.save(self.COLLECTION_NAME, meta)


=======
            info = p.text
            pdf_url = p.a["href"]
            # print (info, pdf_url)
            full_path = os.path.join(archive_path, pdf_url.split("/")[-1])
            urllib.urlretrieve(pdf_url, full_path)
            time.sleep(0.5)

>>>>>>> 59-prca-parse
    def filenamify(self, text):
        allowed_chars = "-_%s%s" % (string.ascii_letters, string.digits)
        return "".join(c if c in allowed_chars else "-" for c in text.lower())

    def get_dates(self, text):
        months = "|".join(calendar.month_name[1:])
        date_range = re.findall(r"(\d+).*?(%s) (\d{4})" % months, text)
        return [datetime.strptime(" ".join(i for i in x), "%d %B %Y").strftime("%Y-%m-%d") for x in date_range]

def fetch():
    FetchAPPC().run()
