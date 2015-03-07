# -*- coding: utf-8 -*-
import logging
import os.path
import requests
from bs4 import BeautifulSoup
from utils import mongo

class ScrapeAPPC:
    def __init__(self):
        self._logger = logging.getLogger('spud')
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.db = mongo.MongoInterface()
        self.PREFIX = "appc"

    def run(self):
        metas = self.db.fetch_all("%s_fetch" % self.PREFIX, paged=False)
        for meta in metas:
            if meta["description"] == "current":
                agency = self.scrape_current(meta)
                self.db.save("%s_scrape" % self.PREFIX, agency)
            else:
                # TODO: Scrape PDFs
                # agencies = self.scrape_pdf(meta)
                pass

    def scrape_current(self, meta):
        full_path = os.path.join(self.current_path, self.STORE_DIR, meta["date_to"], meta["filename"])
        with open(full_path) as f:
            html = f.read()
        soup = BeautifulSoup(html).find(class_="member-profile")

        name = [x for x in soup.find("h1").stripped_strings][0]

        address_soups = soup.find(class_="profile-address").find_all("tr")[1:]
        addresses = []
        contacts = []
        for address_soup in address_soups:
            address, contact = [[x for x in y.stripped_strings] for y in address_soup.find_all("td")]
            if address != []:
                addresses.append(address)
            if contact != []:
                contacts.append(contact)

        country_soup = soup.find(class_="profile-country")
        countries = [x.text for x in country_soup.find_all("li")] if country_soup else []

        staff_soup = soup.find(class_="profile-staff")
        staff = [x.text for x in staff_soup.find_all("li")] if staff_soup else []

        clients = {}
        client_soups = soup.find_all(class_="profile-clients")
        for client_soup in client_soups:
            client_table_heading = client_soup.find("th").text
            if "Pro-Bono Clients" in client_table_heading:
                client_type = "pro-bono"
            elif "UK PA consultancy" in client_table_heading:
                client_type = "consultancy"
            elif "UK monitoring" in client_table_heading:
                client_type = "monitoring"
            else:
                raise Exception("Unknown client type: '%s'" % client_table_heading)
            clients[client_type] = [x.text for x in client_soup.find_all("li")]

        return {
            "name": name,
            "date_from": meta["date_from"],
            "date_to": meta["date_to"],
            "addresses": addresses,
            "contacts": contacts,
            "countries": countries,
            "staff": staff,
            "clients": clients,
            "meta": {k: v for k, v in meta.items() if k in ["source", "linked_from", "fetched"]}
        }

def scrape():
    ScrapeAPPC().run()
