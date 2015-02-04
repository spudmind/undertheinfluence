# -*- coding: utf-8 -*-
import os
import logging
from lxml import objectify
from utils import mongo


current_path = os.path.dirname(os.path.abspath(__file__))


class MPsInterestsScraper():
    def __init__(self):
        self._logger = logging.getLogger('spud')

    def run(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.scraped_mps_interests
        self.data = '/data/regmem'

        # regmem data is produced by the parlparse project which dumps
        # http://www.publications.parliament.uk/pa/cm/cmregmem/memi0910.htm
        # into an xml file. Each file stored one day's recorded interests

        xml_data = current_path + self.data + "/"
        for f in os.listdir(xml_data):
            # scrape each file for interests data
            self.scrape_xml(xml_data, f)

    def scrape_xml(self, xml_path, file_name):
        # the hierarchy of the file to be scraped is:
        # regmem /member name > category > record > items
        # regmem contains 1 or more categories
        # category contains one or more records
        # record is the registered interest & is comprised of many items

        with open(xml_path + file_name) as f:
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
            "file_name": file_name.split(".")[0],
            "contents": contents
        }
        self.cache_data.save(data)

    def scrape_category(self, category):
        self._logger.debug("\t *%s" % category.attrib["name"].strip())
        records = []
        for record in category.getchildren():
            # combine multiple items into a single record
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

    @staticmethod
    def scrape_item(items):
        string = u""
        for x in items.getchildren():
            if x.text is not None:
                string += x.text
            if x.getchildren():
                for y in x.getchildren():
                    if y.text is not None:
                        string += y.text
        return string.strip()
