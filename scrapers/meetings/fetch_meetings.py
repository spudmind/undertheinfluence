# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import os.path
import requests
import time
import urllib
from bs4 import BeautifulSoup
from utils import mongo


class FetchMeetings:
    def __init__(self, **kwargs):
        # fetch the logger
        self._logger = logging.getLogger("spud")
        self.BASE_URL = "https://www.gov.uk"
        # initial search query stuff
        self.search_term = "meetings"
        self.search_filter = "transparency-data"
        # database stuff
        self.db = mongo.MongoInterface()
        self.COLLECTION_NAME = "meetings_fetch"
        if kwargs["refreshdb"]:
            self.db.drop(self.COLLECTION_NAME)
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        # if True, avoid downloading where possible
        self.dryrun = kwargs["dryrun"]

    def fetch_all_publications(self):
        self._logger.debug("Searching %s for '%s' with filter '%s' ..." % (self.BASE_URL, self.search_term, self.search_filter))
        search_tmpl = "%s/government/publications?keywords=%s&publication_filter_option=%s&page=%%d" % (self.BASE_URL, urllib.quote_plus(self.search_term), self.search_filter)
        page = 1
        total_pages = "unknown"
        collections = {}
        publications = {}
        while True:
            if total_pages != "unknown" and page > total_pages:
                # no more search results
                break
            # search gov.uk for results
            self._logger.debug("  Fetching results page %d / %s ..." % (page, total_pages))
            r = requests.get(search_tmpl % page)
            time.sleep(0.5)
            soup = BeautifulSoup(r.text)
            if total_pages == "unknown":
                total_pages = int(soup.find(class_="page-numbers").text[5:])
            publication_soups = soup.find_all(class_="document-row")

            for pub_soup in publication_soups:
                # find collections (we'll use these to find more publications)
                collection_soup = pub_soup.find(class_="document-collections")
                if collection_soup:
                    collection_text = collection_soup.a.text
                    collection_url = "%s%s" % (self.BASE_URL, collection_soup.a["href"])
                    if collection_url not in collections and self.search_term in collection_text.lower():
                        collections[collection_url] = {
                            "url": collection_url,
                            "name": collection_text,
                        }
                    continue

                # any remaining publications are not part of a collection
                pub_title = pub_soup.h3.a
                pub_url = "%s%s" % (self.BASE_URL, pub_title["href"])
                if self.search_term in pub_title.text.lower() and pub_url not in publications:
                    department = pub_soup.find(class_="organisations")
                    if department.abbr is not None:
                        department = department.abbr["title"]
                    else:
                        department = department.text
                    publications[pub_url] = {
                        "source": {
                            "linked_from_url": pub_url,
                        },
                        "collection": None,
                        "title": pub_title.text,
                        "published_at": pub_soup.find(class_="public_timestamp").text.strip(),
                        "department": department,
                    }

            page += 1
        self._logger.debug("Found %d collections, and %d publications not part of collections." % (len(collections), len(publications)))

        publications = self.fetch_pubs_from_collections(collections.values(), publications)
        return publications.values()

    def fetch_pubs_from_collections(self, collections, publications={}):
        self._logger.debug("Searching %d collections for more publications ..." % len(collections))
        for collection in collections:
            r = requests.get(collection["url"])
            time.sleep(0.5)
            soup = BeautifulSoup(r.text)
            department = soup.find(class_="organisation-link").text
            publication_soups = soup.find_all(class_="publication")
            for pub_soup in publication_soups:
                pub_title = pub_soup.h3.a
                pub_url = "%s%s" % (self.BASE_URL, pub_title["href"])
                if self.search_term in pub_title.text.lower() and pub_url not in publications:
                    publications[pub_url] = {
                        "source": {
                            "linked_from_url": pub_url,
                        },
                        "collection": collection["name"],
                        "title": pub_title.text,
                        "published_at": pub_soup.find(class_="public_timestamp").text,
                        "department": department,
                    }
        self._logger.debug("Done searching.")
        return publications

    def fetch_file(self, url, filename):
        self._logger.debug("  Fetching: %s" % url)
        full_path = os.path.join(self.current_path, self.STORE_DIR, filename)
        urllib.urlretrieve(url, full_path)
        time.sleep(0.5)

    def save_to_db(self, publication):
        publication["source"]["fetched"] = False
        # existing = self.db.find_one(self.COLLECTION_NAME, {"url": publication["source"]["url"]})
        # if existing is None:
        self.db.save(self.COLLECTION_NAME, publication, manipulate=False)

    def get_all_unfetched(self):
        all_not_fetched = []
        page = 1
        while True:
            not_fetched, meta = self.db.query(self.COLLECTION_NAME, query={"source.fetched": False}, page=page)
            all_not_fetched += not_fetched
            page += 1
            if not meta["has_more"]:
                return all_not_fetched

    def run(self):
        publications = self.fetch_all_publications()
        self._logger.debug("Searching %d publication pages for attachments ..." % len(publications))
        for pub in publications:
            r = requests.get(pub["source"]["linked_from_url"])
            time.sleep(0.5)
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
                    self._logger.error(attachment_soup)
                    raise Exception("Unknown attachment type.")
                attachment["source"]["url"] = "%s%s" % (self.BASE_URL, rel_url)
                attachment["filename"] = os.path.join("-".join(rel_url.split("/")[-2:]))
                self.save_to_db(attachment)

            if attachment_soups == []:
                # the data is inline - embedded in the page.
                # NB this is very unusual.
                pub["source"]["url"] = pub["source"]["linked_from_url"]
                pub["filename"] = os.path.join("%s.html" % pub["source"]["url"].split("/")[-1])
                pub["file_type"] = "HTML"
                self.save_to_db(pub)

        self._logger.debug("Found %d attachments in total." % self.db.count(self.COLLECTION_NAME))

        if not self.dryrun:
            not_fetched = self.get_all_unfetched()
            self._logger.debug("Fetching %d attachments ..." % len(not_fetched))
            for pub in not_fetched:
                self.fetch_file(pub["source"]["url"], pub["filename"])
                pub["source"]["fetched"] = str(datetime.now())
                self.db.update(self.COLLECTION_NAME, {"source.url": pub["source"]["url"]}, pub)
            self._logger.debug("Attachments fetched.")


def fetch(**kwargs):
    # TODO! this is temporary!
    # import requests_cache
    # requests_cache.install_cache("meetings")
    FetchMeetings(**kwargs).run()
