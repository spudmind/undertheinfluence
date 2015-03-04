# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import os.path
import requests
import time
import urllib
from bs4 import BeautifulSoup
from utils import mongo


class FetchMeetings():
    def __init__(self):
        # fetch the logger
        self._logger = logging.getLogger("spud")
        self.BASE_URL = "https://www.gov.uk"
        # initial search query stuff
        self.search_term = "meetings"
        self.search_filter = "transparency-data"
        # database stuff
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "meetings_fetch"
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))

    def fetch_all_publications(self):
        search_tmpl = "%s/government/publications?keywords=%s&publication_filter_option=%s&page=%%d" % (self.BASE_URL, urllib.quote_plus(self.search_term), self.search_filter)
        page = 1
        collections = {}
        publications = {}
        while True:
            r = requests.get(search_tmpl % page)
            # rate limit requests
            # time.sleep(0.5)
            soup = BeautifulSoup(r.text)
            publication_soups = soup.find_all(class_="document-row")
            if publication_soups == []:
                # no more search results
                break

            for pub_soup in publication_soups:
                collection_soup = pub_soup.find(class_="document-collections")
                if collection_soup:
                    collection_text = collection_soup.a.text
                    collection_url = "%s%s" % (self.BASE_URL, collection_soup.a["href"])
                    if collection_url not in collections and self.search_term in collection_text.lower():
                        collections[collection_url] = {
                            "url": collection_url,
                            "title": collection_soup.a.text,
                        }
                    continue
                pub_title = pub_soup.h3.a
                pub_url = "%s%s" % (self.BASE_URL, pub_title["href"])
                if self.search_term in pub_title.text.lower() and pub_url not in publications:
                    department = pub_soup.find(class_="organisations")
                    if department.abbr is not None:
                        department = department.abbr["title"]
                    else:
                        department = department.text
                    publications[pub_url] = {
                        "linked_from": pub_url,
                        "title": pub_title.text,
                        "published_at": pub_soup.find(class_="public_timestamp").text.strip(),
                        "department": department,
                    }

            page += 1
        self._logger.debug("Fetched %d collections, and %d publications not part of collections" % (len(collections), len(publications)))

        publications = self.fetch_collections(collections.values(), publications)
        return publications.values()

    def fetch_collections(self, collections, publications={}):
        for collection in collections:
            r = requests.get(collection["url"])
            # rate limit requests
            # time.sleep(0.5)
            soup = BeautifulSoup(r.text)
            department = soup.find(class_="organisation-link").text
            publication_soups = soup.find_all(class_="publication")
            for pub_soup in publication_soups:
                pub_title = pub_soup.h3.a
                pub_url = "%s%s" % (self.BASE_URL, pub_title["href"])
                if self.search_term in pub_title.text.lower() and pub_url not in publications:
                    publications[pub_url] = {
                        "linked_from": pub_url,
                        "title": pub_title.text,
                        "published_at": pub_soup.find(class_="public_timestamp").text,
                        "department": department,
                    }
        return publications

    def fetch_file(self, url, filename):
        full_path = os.path.join(self.current_path, self.STORE_DIR, filename)
        urllib.urlretrieve(url, full_path)
        # rate limit requests
        time.sleep(0.5)

    def save_to_db(self, publication):
        publication["fetched"] = False
        publication["scraped"] = False
        existing = self.db.find_one(self.COLLECTION_NAME, {"url": publication["url"]})
        if existing is None:
            self.db.save(self.COLLECTION_NAME, publication, manipulate=False)

    def get_all_unfetched(self):
        all_not_fetched = []
        page = 1
        while True:
            not_fetched, meta = self.db.query(self.COLLECTION_NAME, {"fetched": False}, page=page)
            all_not_fetched += not_fetched
            page += 1
            if not meta["has_more"]:
                return all_not_fetched

    def run(self):
        publications = self.fetch_all_publications()
        for pub in publications:
            r = requests.get(pub["linked_from"])
            # rate limit requests
            # time.sleep(0.5)
            soup = BeautifulSoup(r.text)
            attachment_soups = soup.find_all(class_="attachment")
            for attachment_soup in attachment_soups:
                attachment_title = attachment_soup.h2.text
                if self.search_term not in attachment_title.lower():
                    continue
                attachment = pub.copy()
                attachment["title"] = attachment_title
                download_soup = attachment_soup.find(class_="download")
                if download_soup is not None:
                    # download link (usually to a csv) is available
                    rel_url = download_soup.a["href"]
                    attachment["file_type"] = rel_url.split(".")[-1].upper()
                elif attachment_soup.h2.a is not None:
                    # heading link (usually to a pdf)
                    rel_url = attachment_soup.h2.a["href"]
                    attachment["file_type"] = attachment_soup.find(class_="type").text
                else:
                    print attachment_soup
                    raise Exception("Unknown attachment type.")
                attachment["url"] = "%s%s" % (self.BASE_URL, rel_url)
                attachment["filename"] = "-".join(rel_url.split("/")[-2:])
                self.save_to_db(attachment)
            if attachment_soups == []:
                # the data is inline - embedded in the page.
                # NB this is very unusual.
                pub["url"] = pub["linked_from"]
                pub["filename"] = "%s.html" % pub["url"].split("/")[-1]
                pub["file_type"] = "HTML"
                self.save_to_db(pub)
        not_fetched = self.get_all_unfetched()
        for pub in not_fetched:
            self.fetch_file(pub["url"], pub["filename"])
            pub["fetched"] = str(datetime.now())
            self.db.update(self.COLLECTION_NAME, {"url": pub["url"]}, pub)

def fetch():
    # TODO! this is temporary!
    import requests_cache
    requests_cache.install_cache("meetings")
    FetchMeetings().run()
