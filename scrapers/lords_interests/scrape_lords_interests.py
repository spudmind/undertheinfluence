# -*- coding: utf-8 -*-
import logging
import os.path
import re
import simplejson
from utils import mongo


class ScrapeLordsInterests:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.PREFIX = "lords_interests"
        # database stuff
        self.db = mongo.MongoInterface()
        if kwargs["refreshdb"]:
            self.db.drop("%s_scrape" % self.PREFIX)

    def run(self):
        self._logger.info("Importing Lords interests ...")
        metas = self.db.fetch_all("%s_fetch" % self.PREFIX, paged=False)
        for meta in metas:
            full_path = os.path.join(self.current_path, meta["filename"])
            with open(full_path) as f:
                j = simplejson.load(f)["Members"]
            j = {} if j is None else j
            for lord in listify(j.get("Member", [])):
                self.scrape_interests(lord, meta)
        self._logger.info("Done importing Lords interests.")

    def scrape_interests(self, lord, meta):
        member_id = lord["@Member_Id"]
        name = lord["FullTitle"]
        preferred_names = listify(lord["PreferredNames"]["PreferredName"])
        aliases = {" ".join([preferred_name[x] for x in ["Forename", "MiddleNames", "Surname"] if preferred_name.get(x, None) is not None]): None for preferred_name in preferred_names}.keys()

        interests = []
        interest_categories = lord["Interests"]
        if interest_categories:
            for interest_category in listify(interest_categories["Category"]):
                category_name = interest_category["@Name"]
                if category_name == "Nil":
                    # there's no registrable interests, so jump out
                    continue

                # # NB: the cat ID here is probably more reliable
                # cat_id = interest_category["@Id"]
                category_name = re.match("Category \d+: (.*)", category_name).group(1)

                records = [{
                    "interest": interest["RegisteredInterest"],
                    "created": interest["Created"],
                    "amended": interest["@LastAmendment"],
                } for interest in listify(interest_category["Interest"])]
                interests.append({
                    "records": records,
                    "category_name": category_name,
                })

        data = {
            "member_id": member_id,
            "name": name,
            "aliases": aliases,
            "interests": interests,
            "source": meta["source"]
        }
        self.db.update("%s_scrape" % self.PREFIX, {"member_id": data["member_id"]}, data, upsert=True)

# wrap non-lists in a list
def listify(l):
    if isinstance(l, list):
        return l
    else:
        return [l]

def scrape(**kwargs):
    ScrapeLordsInterests(**kwargs).run()
