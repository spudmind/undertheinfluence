# -*- coding: utf-8 -*-
import logging
import os.path
import requests
from bs4 import BeautifulSoup
from utils import mongo


class ScrapeAPPC:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        # database stuff
        self.db = mongo.MongoInterface()
        self.PREFIX = "appc"
        if kwargs["refreshdb"]:
            self.db.drop("%s_scrape" % self.PREFIX)

    def run(self):
        self._logger.info("Scraping APPC ...")
        metas = self.db.fetch_all("%s_fetch" % self.PREFIX, paged=False)
        for meta in metas:
            if meta["filename"].endswith(".html"):
                agency = self.scrape_current(meta)
                spec = {"name": agency["name"], "date_range": agency["date_range"]}
                self.db.update("%s_scrape" % self.PREFIX, spec, agency, upsert=True)
            else:
                # TODO: Scrape PDFs
                # agencies = self.scrape_pdf(meta)
                pass
        self._logger.info("Done scraping APPC.")

    def scrape_current(self, meta):
        self._logger.info("  Scraping '%s' ...." % meta["filename"])
        full_path = os.path.join(self.current_path, meta["filename"])
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
        countries = [x.text.strip() for x in country_soup.find_all("li")] if country_soup else []

        staff_soup = soup.find(class_="profile-staff")
        all_staff = [x.text.strip() for x in staff_soup.find_all("li")] if staff_soup else []
        staff = {"has_pass": [], "no_pass": []}
        for staff_name in all_staff:
            if staff_name.endswith(" *"):
                staff["has_pass"].append(staff_name[:-2].strip())
            else:
                staff["no_pass"].append(staff_name)

        clients = {"pro-bono": [], "consultancy": [], "monitoring": []}
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
            for client in client_soup.find_all("li"):
                client = [c for c in client.stripped_strings]
                clients[client_type].append({
                    "name": client[0],
                    "description": client[2] if len(client) > 1 else None
                })

        return {
            "name": name,
            "date_range": meta["date_range"],
            "addresses": addresses,
            "contacts": contacts,
            "countries": countries,
            "staff": staff,
            "clients": clients,
            "source": meta["source"],
        }


def scrape(**kwargs):
    ScrapeAPPC(**kwargs).run()
