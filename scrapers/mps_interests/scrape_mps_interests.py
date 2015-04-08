# -*- coding: utf-8 -*-
import os.path
import logging
from lxml import objectify
from utils import mongo


class ScrapeMPsInterests:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        # database stuff
        self.db = mongo.MongoInterface()
        self.PREFIX = "mps_interests"
        if kwargs["refreshdb"]:
            self.db.drop("%s_scrape" % self.PREFIX)

    def run(self):
        metas = self.db.fetch_all("%s_fetch" % self.PREFIX, paged=False)
        for meta in metas:
            # scrape each file for interests data
            self.scrape_xml(meta)

    def scrape_xml(self, meta):
        # the hierarchy of the file to be scraped is:
        # regmem /member name > category > record > items
        # regmem contains 1 or more categories
        # category contains one or more records
        # record is the registered interest & is comprised of many items

        with open(os.path.join(self.current_path, meta["filename"])) as f:
            xml = f.read()
        root = objectify.fromstring(xml)
        contents = []
        for mp in root.getchildren():
            self._logger.debug(mp.attrib["membername"])
            categories = []
            for category in mp.getchildren():
                if "name" in category.attrib:
                    if "." in category.attrib["name"]:
                        category_name = category.attrib["name"].replace(".", "_")
                    else:
                        category_name = category.attrib["name"]
                    cat_data = {
                        "category_name": category_name.strip(),
                        "records": self.scrape_category(category)
                    }
                    categories.append(cat_data)
            self._logger.debug("\n---")
            mp_data = {
                "mp": mp.attrib["membername"],
                "interests": categories
            }
            contents.append(mp_data)
        data = {
            "contents": contents,
            "date": meta["date"],
            "source": meta["source"],
        }
        self.db.update("%s_scrape" % self.PREFIX, {"date": meta["date"]}, data)

    def scrape_category(self, category):
        self._logger.debug("\t *%s" % category.attrib["name"].strip())
        records = []
        for record in category.getchildren():
            # combine multiple items into a record list
            items = []
            for item in record.getchildren():
                text = u""
                if item.text is not None:
                    text += item.text
                if item.getchildren():
                    text += self.scrape_item(item)
                items.append(text)
                self._logger.debug("\t\t%s" % text.strip())
            self._logger.debug("\t\t---")
            records.append(items)
        return records

    def scrape_item(self, items):
        string = u""
        for x in items.getchildren():
            if x.text is not None:
                string += x.text
            if x.getchildren():
                for y in x.getchildren():
                    if y.text is not None:
                        string += y.text
        return string.strip()

def scrape(**kwargs):
    ScrapeMPsInterests(**kwargs).run()
