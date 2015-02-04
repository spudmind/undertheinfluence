# -*- coding: utf-8 -*-
import re
import logging
from utils import mongo
from utils import entity_extraction
from utils import entity_resolver


class LordsInterestsParser:
    def __init__(self):
        self._logger = logging.getLogger('spud')

    def run(self):
        self.entity_extractor = entity_extraction.NamedEntityExtractor()
        self.entity_resolver = entity_resolver.MasterEntitiesResolver()
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.scraped_lords_interests
        self.all_lord_interests = []
        self.money_search = ur'([£$€])(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        self.date_search = ur'(\d{1,2}\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4})'

        self.all_lord_interests = list(self.cache_data.find())
        for lord in self.all_lord_interests:
            lord_name = lord["member_title"]
            resolved_name = self.entity_resolver.find_lord(lord_name)
            self._logger.debug("\n%s / %s" % (resolved_name, lord_name))
            categories = self._get_category_data(lord["interests"])
            lord_data = {
                "lord": resolved_name,
                "interests": categories
            }
            #self.cache.db.parsed_lords_interests.save(lord_data)

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
        category_name = data["category_name"]
        self._show_record(data)
        self._parse_standard(data)

    def _parse_standard(self, data):
        records = []
        for record in data["records"]:
            company_name = self.entity_resolver.find_donor(record)
            self._logger.debug(" ---> donor: %s" % company_name)
            entry = {
                "interest": company_name,
                "raw_record": record
            }
            records.append(entry)
        return records

    def _find_dates(self, data):
        dates = re.findall(self.date_search, data)
        if dates:
            return dates
        else:
            return None

    def _show_record(self, data):
        self._logger.debug("   * %s" % data["category_name"])
        for item in data["records"]:
            self._logger.debug("     %s" % item)
        # self._logger.debug("---")

    @staticmethod
    def _split_if_colon(text):
        result = text.strip()
        if len(text.split(":")) > 1:
            result = text.split(":")[1].strip()
        return result

    def _print_out(self, key, value):
        self._logger.debug("  %-30s%-20s" % (key, value))
