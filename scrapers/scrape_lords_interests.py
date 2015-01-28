# -*- coding: utf-8 -*-

import json
import requests
import sys
import os.path
import re

from lxml import etree

# Path hack.
sys.path.insert(0, os.path.abspath('..'))

from utils import mongo

current_path = os.path.dirname(os.path.abspath(__file__))


class LordsInterestsScraper():
    def __init__(self):
        self.mongo = mongo.MongoInterface()
        self.mongo_db = self.mongo.db.scraped_lords_interests
        self.cache_path = os.path.join(current_path, 'data', 'reglords')
        self.url = "http://data.parliament.uk/membersdataplatform/services/mnis/members/query/house=Lords/Interests%7CPreferredNames/"

    def run(self):
        # TODO: we're not doing dates at the moment...
        # It's trivial to modify the query so we fetch a date range,
        # but it's likely we'll just get loads and loads of overlap.
        # It’s not obvious to me how to fix this...
        file_name = "current-lords"

        full_path = os.path.join(self.cache_path, '%s.xml' % file_name)
        if os.path.exists(full_path):
            with open(full_path) as f:
                xml = f.read()
        else:
            r = requests.get(self.url)
            xml = r.text.encode('utf-8')
            with open(full_path, 'w') as f:
                f.write(xml)

        root = etree.fromstring(xml)
        members = root.findall("Member")

        self.scrape_xml(members, file_name)

    def scrape_xml(self, members, file_name):
        contents = []
        for member in members:
            interests = []
            preferred_name = member.find("PreferredNames").find("PreferredName")
            member_name = "%s %s" % (preferred_name.find("Forename").text, preferred_name.find("Surname").text)
            member_id = member.get("Member_Id")

            categories_tree = member.find("Interests").findall("Category")
            for category_tree in categories_tree:
                interests_tree = category_tree.findall("Interest")
                records = []
                # NB: the cat ID here is probably more reliable
                cat_id = category_tree.get("Id")
                if category_tree.get("Name") == 'Nil':
                    # there's no registrable interests, so jump out
                    continue
                cat_name = re.search('Category \d+: (.*)', category_tree.get("Name")).group(1)

                for interest_tree in interests_tree:
                    # print interest_tree.find("Created").text
                    records.append(interest_tree.find("RegisteredInterest").text)
                interests.append({
                    "records": records,
                    "category_name": cat_name,
                })

            contents.append({
                "member_id": member_id,
                "name": member_name,
                "interests": interests,
            })

        data = {
            "file_name": file_name,
            "contents": contents,
        }
        self.mongo_db.save(data)
