# -*- coding: utf-8 -*-
import logging
from utils import mongo
from data_models import models


class GraphLordsInterests():
    def __init__(self):
        self._logger = logging.getLogger('spud')

    def run(self):
        self.db = mongo.MongoInterface()
        self.data_models = models
        all_lords = self.db.fetch_all('parsed_lords_interests', paged=False)
        for doc in all_lords:
            self._graph_interests(doc)

    def _graph_interests(self, node):
        self._logger.debug("\n..................")
        self._logger.debug(node["lord"])
        # self._logger.debug("\n%s\n" % node)
        lord = self._find_lord(node["lord"])
        self._parse_categories(lord, node["interests"])
        self._logger.debug("..................")

    def _parse_categories(self, lord, categories):
        for category in categories:
            category_name = category["category_name"]
            self._logger.debug(category_name)
            new_category = self._create_category(lord.name, category_name)
            lord.link_interest_category(new_category)
            self._logger.debug("*")
            self._create_graph(lord, new_category, category["category_records"])

    def _create_graph(self, lord, category, records):
        if records:
            for record in records:
                self._print_out("interest", record["interest"])
                if record["interest"] and record["interest"] != "None":
                    funding_relationship = self._create_relationship(
                        lord.name,
                        record["interest"]
                    )
                    new_interest = self._create_interest(record["interest"])
                    new_interest.set_interest_details()
                    category.link_relationship(funding_relationship)
                    funding_relationship.link_donor(new_interest)
                    funding_relationship.update_raw_record(record["raw_record"])
                    if "created" in record and record["created"]:
                            funding_relationship.set_registered_date(record["created"])
                    if "position" in record:
                        funding_relationship.vertex["position"] = record["position"]
                    funding_relationship.vertex.push()
                else:
                    self._logger.debug("** NO INTEREST ** ")
                    self._logger.debug("** NO INTEREST ** ")
                self._logger.debug("-\n")

    def _create_category(self, name, category):
        props = {"lord": name, "category": category}
        category_name = u"{} - {}".format(name, category)
        new_category = self.data_models.InterestCategory(category_name)
        if not new_category.exists:
            new_category.create()
        new_category.update_category_details(props)
        return new_category

    def _create_relationship(self, name, donor):
        props = {"recipient": name, "donor": donor}
        category_name = u"{} and {}".format(donor, name)
        new_relationship = self.data_models.FundingRelationship(category_name)
        if not new_relationship.exists:
            new_relationship.create()
        new_relationship.set_category_details(props)
        return new_relationship

    def _create_interest(self, interest):
        if isinstance(interest, list):
            interest = interest[0]
        entry = self.data_models.RegisteredInterest(interest)
        if not entry.exists:
            entry.create()
        return entry

    def _find_lord(self, lord):
        new_lord = self.data_models.Lord(lord)
        if not new_lord.exists:
            self._logger.debug("%s *not found*" % lord)
            new_lord.create()
        return new_lord

    def _print_out(self, key, value):
        self._logger.debug("  %-25s%-25s" % (key, value))

    @staticmethod
    def _is_remuneration(record):
        result = False
        if "remuneration" in record:
            if record["remuneration"] and \
                    len(record["remuneration"]) > 0:
                    result = True
        return result

    @staticmethod
    def convert_to_number(amount):
        if "," in amount:
            amount = amount.replace(",", "")
        if "." in amount:
            amount = amount.split(".")[0]
        if amount.isdigit():
            return int(amount)
        else:
            return 0
