# -*- coding: utf-8 -*-
import re
import logging
from utils import mongo
# from utils import entity_extraction
from utils import entity_resolver


class LordsInterestsParser:
    def __init__(self):
        self._logger = logging.getLogger('spud')

    def run(self):
        self.entity_resolver = entity_resolver.MasterEntitiesResolver()
        self.db = mongo.MongoInterface()

        all_interests = self.db.fetch_all('scraped_lords_interests', paged=False)
        for lord in all_interests:
            lord_name = lord["member_title"]
            resolved_name = self.entity_resolver.find_lord(lord_name)
            self._logger.debug("\n%s / %s" % (resolved_name, lord_name))
            if len(lord["interests"]) > 0:
                # skip Lords who do not have any interests
                categories = self._get_category_data(lord["interests"])
                lord_data = {
                    "lord": resolved_name,
                    "interests": categories
                }
                self.db.save('parsed_lords_interests', lord_data)

    def _get_category_data(self, categories):
        categories_data = []
        for category in categories:
            cat_data = {
                "category_name": category["category_name"],
                "category_records": self._parse_category(category)
            }
            # self._logger.debug("\n%s\n" % cat_data)
            categories_data.append(cat_data)
            self._logger.debug("---")
        return categories_data

    def _parse_category(self, data):

        # individual categories to conform to fit one of two parsers
        # this function picks the appropriate parser for each category

        category_name = data["category_name"].lower()
        self._show_record(data)
        if "non-financial interests" in category_name:
            #pass
            return self._parse_simple(data)
        elif "remunerated employment" in category_name:
            #pass
            return self._parse_simple(data)
        elif "directorships" in category_name:
            #pass
            return self._parse_simple(data)
        else:
            #pass
            return self._parse_standard(data)

    def _parse_simple(self, data):

        # these interests mostly follow the following format:
        # Job Title, Interest or
        # Board Position, Board, Interest
        # Speaking Engagement, Date, Interest, Location

        records = []
        for record in data["records"]:
            interest_name = None
            position = None
            # remove (extraneous interest / company descriptions)
            parsed_interest = self._remove_extraneous(record["interest"])
            parsed_interest = parsed_interest.split(",")
            if len(parsed_interest) == 1:
                interest_name = parsed_interest[0].strip()
            if len(parsed_interest) == 2:
                position = parsed_interest[0].strip()
                interest_name = parsed_interest[1].strip()
            if len(parsed_interest) > 2:
                position = parsed_interest[0].strip()
                interest_name = parsed_interest[1].strip()
                if "speaking engagement" in parsed_interest[0].lower():
                    interest_name = parsed_interest[2].strip()
                if "board" in interest_name.lower():
                    interest_name = parsed_interest[2].strip()
            self._logger.debug(" interest: %s" % interest_name)
            if interest_name:
                entry = {
                    "position": position,
                    "interest": interest_name,
                    "raw_record": record["interest"],
                    "created": self._get_date(record["created"]),
                    "amended": self._get_date(record["amended"])
                }
                records.append(entry)
        return records

    def _parse_standard(self, data):

        # extract interest names using donor entity resolver

        records = []
        for record in data["records"]:
            interest_name = self.entity_resolver.find_donor(record["interest"])
            # if no interest is found, skip record
            if interest_name:
                self._logger.debug(" interest: %s" % interest_name)
                entry = {
                    "interest": interest_name,
                    "raw_record": record["interest"],
                    "created": self._get_date(record["created"]),
                    "amended": self._get_date(record["amended"])
                }
                records.append(entry)
        return records

    def _show_record(self, data):
        self._logger.debug("   * %s" % data["category_name"])
        for item in data["records"]:
            self._logger.debug("     %s" % item["interest"])
            self._logger.debug("     %s" % item["created"])
            self._logger.debug("     %s" % item["amended"])
            self._logger.debug(" ")

    @staticmethod
    def _get_date(data):
        date = None
        if data:
            date = data.split("T")[0]
        return date

    @staticmethod
    def _remove_extraneous(data):
        data = data.replace('"', "", 5)
        if "category 4(a)" in data:
            data = data.strip("category 4(a)")
        try:
            return re.sub('\(.+?\)\s*', '', data)
        except TypeError:
            print "Error", data

    def _print_out(self, key, value):
        self._logger.debug("  %-30s%-20s" % (key, value))
