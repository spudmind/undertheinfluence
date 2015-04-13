# -*- coding: utf-8 -*-
import logging
import json
from data_models.influencers_models import FundingRelationship
from data_models.influencers_models import InterestCategory
from data_models.influencers_models import RegisteredInterest
from data_models.influencers_models import InterestDetail
from utils import mongo
from data_models import government_models


class GraphLordsInterests():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.data_models = government_models
        self.PREFIX = "lords_interests"

    def run(self):
        all_lords = self.db.fetch_all("%s_parse" % self.PREFIX, paged=False)
        for doc in all_lords:
            self._graph_interests(doc)

    def _graph_interests(self, node):
        self._logger.debug("\n..................")
        self.current_detail = {
            "lord": node["lord"],
            "source": node["source"],
        }

        lord = self._find_lord(node["lord"])

        self._logger.debug(node["lord"])
        self._parse_categories(lord, node["interests"])

    def _parse_categories(self, lord, categories):
        for category in categories:
            category_name = category["category_name"]
            self.current_detail["category"] = category_name
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
                    date = None
                    position = None

                    funding_relationship = self._create_relationship(
                        lord.name,
                        record["interest"]
                    )
                    funding_relationship.set_relationship_details()
                    new_interest = self._create_interest(record["interest"])
                    new_interest.set_interest_details()

                    if "created" in record and record["created"]:
                        date = record["created"]

                    if "position" in record:
                        position = record["position"]

                    category.link_relationship(funding_relationship)
                    funding_relationship.link_contributor(new_interest)

                    summary = u"{} - {} - {} - {}".format(
                        record["interest"],
                        self.current_detail["category"],
                        self.current_detail["lord"],
                        date
                    )

                    meta = {
                        "source_url": self.current_detail["source"]["url"],
                        "source_linked_from": self.current_detail["source"]["linked_from_url"],
                        "source_fetched": str(self.current_detail["source"]["fetched"]),
                        "contributor": record["interest"],
                        "recipient": self.current_detail["lord"],
                        "position": position,
                        "registered": date
                    }

                    interest_detail = InterestDetail(summary)
                    if not interest_detail.exists:
                        interest_detail.create()
                        interest_detail.set_interest_details(meta)

                        funding_relationship.link_interest_detail(interest_detail)

                        if date:
                            interest_detail.set_registered_date(date)

                    funding_relationship.update_raw_record(record["raw_record"])
                else:
                    self._logger.debug("** NO INTEREST ** ")
                    self._logger.debug("** NO INTEREST ** ")
                self._logger.debug("-\n")

    def _create_category(self, name, category):
        props = {"lord": name, "category": category}
        category_name = u"{} - {}".format(name, category)
        new_category = InterestCategory(category_name)
        if not new_category.exists:
            new_category.create()
        new_category.update_category_details(props)
        return new_category

    def _create_relationship(self, name, donor):
        props = {"recipient": name, "donor": donor}
        category_name = u"{} and {}".format(donor, name)
        new_relationship = FundingRelationship(category_name)
        if not new_relationship.exists:
            new_relationship.create()
        new_relationship.set_relationship_details(props)
        return new_relationship

    def _create_interest(self, interest):
        if isinstance(interest, list):
            interest = interest[0]
        entry = RegisteredInterest(interest)
        if not entry.exists:
            entry.create()
        return entry

    def _find_lord(self, lord):
        new_lord = self.data_models.Lord(lord)
        if not new_lord.exists:
            self._logger.debug("%s *not found*" % lord)
            new_lord.create()
            new_lord.set_lord_details({"data_source": "register_of_interests"})
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
