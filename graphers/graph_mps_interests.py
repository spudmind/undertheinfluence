# -*- coding: utf-8 -*-
import logging
import json
from data_models.influencers_models import FundingRelationship
from data_models.influencers_models import InterestCategory
from data_models.influencers_models import RegisteredInterest
from data_models.influencers_models import InterestDetail
from utils import mongo
from data_models import government_models


class GraphMPsInterests():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.data_models = government_models
        self.PREFIX = "mps_interests"
        # database stuff
        self.db = mongo.MongoInterface()
        self.extra_details = [
            "donor_status",
            "purpose",
            "visit_dates",
            "receipt",
            "accepted",
            "nature"
        ]

    def run(self):
        all_mps = self.db.fetch_all("%s_parse" % self.PREFIX, paged=False)
        for doc in all_mps:
            self._graph_interests(doc)

    def _graph_interests(self, node):
        self.current_detail = {"mp": node["mp"]}

        self.current_detail["recorded_date"] = node["date"]

        source_url = node["source"]["url"]
        if not source_url:
            source_url = ""
        self.current_detail["source_url"] = source_url
        self.current_detail["source_linked_from"] = node["source"]["linked_from_url"]
        self.current_detail["source_fetched"] = str(node["source"]["fetched"])

        self._logger.debug("\n..................")
        self._logger.debug(node["mp"])
        self._logger.debug("..................")

        mp = self._find_mp(node["mp"])

        self._parse_categories(mp, node["interests"])
        #self._parse_categories(node["interests"])

    def _find_mp(self, mp):
        new_mp = self.data_models.MemberOfParliament(mp)
        if not new_mp.exists:
            self._logger.debug("%s *not found*" % mp)
            new_mp.create()
            new_mp.set_mp_details({"data_source": "register_of_interests"})
        return new_mp

    # def _parse_categories(self, categories):
    def _parse_categories(self, mp, categories):
        for category in categories:

            self.current_detail["category"] = category["category_name"]
            category_name = category["category_name"]
            new_category = self._create_category(mp.name, category_name)
            mp.link_interest_category(new_category)

            if category_name == "Directorships":
                self._logger.debug(category_name)
                self._graph_list(new_category, category["category_records"])
            elif category_name == "Remunerated directorships":
                self._logger.debug(category_name)
                self._graph_list(new_category, category["category_records"])
            elif category_name == "Remunerated employment, office, profession etc":
                self._logger.debug(category_name)
                self._graph_list(new_category, category["category_records"])
            elif category_name == "Remunerated employment, office, profession, etc_":
                self._logger.debug(category_name)
                self._graph_list(new_category, category["category_records"])
            elif category_name == "Clients":
                if category["category_records"]:
                    self._logger.debug(category_name)
                    # self._graph_unstructured(new_category, category["category_records"])
                    self._create_graph(new_category, category["category_records"])
                # self._create_graph(new_category, category["category_records"])
            elif category_name == "Land and Property":
                pass
            elif category_name == "Shareholdings":
                self._logger.debug(category_name)
                self._graph_unstructured(new_category, category["category_records"])
            elif category_name == "Registrable shareholdings":
                self._logger.debug(category_name)
                self._graph_unstructured(new_category, category["category_records"])
            elif category_name == "Sponsorships":
                self._logger.debug(category_name)
                self._graph_sponsorship(new_category, category["category_records"])
            elif category_name == "Sponsorship or financial or material support":
                self._logger.debug(category_name)
                self._graph_sponsorship(new_category, category["category_records"])
            elif category_name == "Overseas visits":
                self._logger.debug(category_name)
                self._graph_travel(new_category, category["category_records"])
            elif category_name == "Gifts, benefits and hospitality (UK)":
                self._logger.debug(category_name)
                self._graph_gifts(new_category, category["category_records"])
            elif category_name == "Gifts, benefits and hospitality (UK)":
                self._logger.debug(category_name)
                self._graph_gifts(new_category, category["category_records"])
            elif category_name == "Miscellaneous":
                self._logger.debug(category_name)
                self._graph_unstructured(new_category, category["category_records"])
            self._logger.debug("*")

    def _graph_list(self, category, records):
        if records:
            for record in records:
                if record["interest"] and record["interest"] != "None":

                    registered_interest = self._create_interest(record["interest"])
                    registered_interest.set_interest_details()

                    funding_relationship = self._create_relationship(
                        self.current_detail["mp"],
                        record["interest"]
                    )

                    category.link_relationship(funding_relationship)
                    funding_relationship.link_contributor(registered_interest)

                    context = u"{} - {} - {}".format(
                        record["interest"],
                        self.current_detail["category"],
                        self.current_detail["mp"]
                    )

                    meta = {
                        "recorded date": self.current_detail["recorded_date"],
                        "source_url": self.current_detail["source_url"],
                        "source_linked_from": self.current_detail["source_linked_from"],
                        "source_fetched": str(self.current_detail["source_fetched"]),
                        "contributor": record["interest"],
                        "recipient": self.current_detail["mp"],
                    }

                    if len(record["remuneration"]) > 0:
                        for entry in record["remuneration"]:
                            amount = entry["amount"]
                            int_amount = self.convert_to_number(amount)
                            summary = u"{} - £{} - {} - {}".format(
                                context, amount, entry["received"], entry["registered"]
                            )
                            interest_detail = InterestDetail(summary)
                            interest_detail.create()
                            interest_detail.set_interest_details({"amount": int_amount})
                            interest_detail.set_interest_details(meta)
                            # interest_detail.update_raw_record(record["raw_record"])

                            funding_relationship.link_interest_detail(interest_detail)

                            if "received" in entry and entry["received"] != u"Unknown":
                                interest_detail.set_interest_details({"registered": entry["received"]})
                                interest_detail.set_received_date(entry["received"])
                            if "registered" in entry and entry["registered"] != u"Unknown":
                                interest_detail.set_interest_details({"registered": entry["registered"]})
                                interest_detail.set_registered_date(entry["registered"])
                            self._logger.debug(summary)
                    else:
                        interest_detail = InterestDetail(context)
                        interest_detail.create()
                        interest_detail.set_interest_details(meta)
                        # interest_detail.update_raw_record(record["raw_record"])
                        funding_relationship.link_interest_detail(interest_detail)

                        self._logger.debug(context)

    def _graph_unstructured(self, category, records):
        for record in records:
            if record["interest"] and record["interest"] != "None":
                date = None
                if record["registered"]:
                    if len(record["registered"]) == 1:
                        date = record["registered"][0]
                    else:
                        date = record["registered"][-1]

                registered_interest = self._create_interest(record["interest"])
                registered_interest.set_interest_details()

                funding_relationship = self._create_relationship(
                    self.current_detail["mp"],
                    record["interest"]
                )

                category.link_relationship(funding_relationship)
                funding_relationship.link_contributor(registered_interest)

                summary = u"{} - {} - {} - {}".format(
                    record["interest"],
                    self.current_detail["category"],
                    self.current_detail["mp"],
                    date
                )

                meta = {
                    "recorded date": self.current_detail["recorded_date"],
                    "source_url": self.current_detail["source_url"],
                    "source_linked_from": self.current_detail["source_linked_from"],
                    "source_fetched": str(self.current_detail["source_fetched"]),
                    "contributor": record["interest"],
                    "recipient": self.current_detail["mp"],
                }

                interest_detail = InterestDetail(summary)
                interest_detail.create()
                interest_detail.set_interest_details(meta)
                # interest_detail.update_raw_record(record["raw_record"])

                funding_relationship.link_interest_detail(interest_detail)

                if date:
                    interest_detail.set_interest_details({"registered": date})
                    interest_detail.set_registered_date(date)

                self._logger.debug(summary)

    def _graph_sponsorship(self, category, records):
        for record in records:
            if record["interest"] and record["interest"] != "None":
                date = None
                if record["registered"]:
                    if len(record["registered"]) == 1:
                        date = record["registered"][0]
                    else:
                        date = record["registered"][-1]

                registered_interest = self._create_interest(record["interest"])
                registered_interest.set_interest_details()

                funding_relationship = self._create_relationship(
                    self.current_detail["mp"],
                    record["interest"]
                )

                category.link_relationship(funding_relationship)
                funding_relationship.link_contributor(registered_interest)

                meta = {
                    "recorded date": self.current_detail["recorded_date"],
                    "source_url": self.current_detail["source_url"],
                    "source_linked_from": self.current_detail["source_linked_from"],
                    "source_fetched": str(self.current_detail["source_fetched"]),
                    "contributor": record["interest"],
                    "recipient": self.current_detail["mp"],
                    "donor_status": record["donor_status"]
                }

                if "remuneration" in record and record["remuneration"]:
                    for entry in record["remuneration"]:
                        amount = entry
                        int_amount = self.convert_to_number(amount)
                        summary = u"{} - {} - {} - {} - {}".format(
                            record["interest"],
                            self.current_detail["category"],
                            self.current_detail["mp"],
                            amount,
                            date
                        )

                        interest_detail = InterestDetail(summary)
                        interest_detail.create()
                        interest_detail.set_interest_details({"amount": int_amount})
                        interest_detail.set_interest_details(meta)
                        # interest_detail.update_raw_record(record["raw_record"])

                        funding_relationship.link_interest_detail(interest_detail)

                        if date:
                            interest_detail.set_interest_details({"registered": date})
                            interest_detail.set_registered_date(date)

                        self._logger.debug(summary)
                else:
                    summary = u"{} - {} - {} - {}".format(
                        record["interest"],
                        self.current_detail["category"],
                        self.current_detail["mp"],
                        date
                    )

                    interest_detail = InterestDetail(summary)
                    interest_detail.create()
                    interest_detail.set_interest_details(meta)
                    # interest_detail.update_raw_record(record["raw_record"])

                    funding_relationship.link_interest_detail(interest_detail)

                    if date:
                        interest_detail.set_interest_details({"registered": date})
                        interest_detail.set_registered_date(date)

                    self._logger.debug(summary)

    def _graph_travel(self, category, records):
        for record in records:
            if record["interest"] and record["interest"] != "None":
                date = None
                if record["registered"]:
                    if len(record["registered"]) == 1:
                        date = record["registered"][0]
                    else:
                        date = record["registered"][-1]

                registered_interest = self._create_interest(record["interest"])
                registered_interest.set_interest_details()

                funding_relationship = self._create_relationship(
                    self.current_detail["mp"],
                    record["interest"]
                )

                category.link_relationship(funding_relationship)
                funding_relationship.link_contributor(registered_interest)

                meta = {
                    "recorded date": self.current_detail["recorded_date"],
                    "source_url": self.current_detail["source_url"],
                    "source_linked_from": self.current_detail["source_linked_from"],
                    "source_fetched": str(self.current_detail["source_fetched"]),
                    "contributor": record["interest"],
                    "recipient": self.current_detail["mp"],
                    "visit_dates": record["vist_dates"],
                    "purpose": record["purpose"],
                    # "raw_record": record["raw_record"],
                }

                if record["remuneration"] and len(record["remuneration"]) > 0:
                    for entry in record["remuneration"]:
                        amount = entry
                        int_amount = self.convert_to_number(amount)
                        summary = u"{} - {} - {} - {} - {}".format(
                            record["interest"],
                            self.current_detail["category"],
                            self.current_detail["mp"],
                            amount,
                            date
                        )

                        interest_detail = InterestDetail(summary)
                        interest_detail.create()
                        interest_detail.set_interest_details({"amount": int_amount})
                        interest_detail.set_interest_details(meta)
                        # interest_detail.update_raw_record(record["raw_record"])

                        funding_relationship.link_interest_detail(interest_detail)

                        if date:
                            interest_detail.set_interest_details({"registered": date})
                            interest_detail.set_registered_date(date)
                        self._logger.debug(summary)
                else:
                    summary = u"{} - {} - {} - {}".format(
                        record["interest"],
                        self.current_detail["category"],
                        self.current_detail["mp"],
                        date
                    )
                    interest_detail = InterestDetail(summary)
                    interest_detail.create()
                    interest_detail.set_interest_details(meta)
                    # interest_detail.update_raw_record(record["raw_record"])

                    funding_relationship.link_interest_detail(interest_detail)

                    if date:
                        interest_detail.set_interest_details({"registered": date})
                        interest_detail.set_registered_date(date)

    def _graph_gifts(self, category, records):
        for record in records:
            if record["interest"] and record["interest"] != "None":
                registered = None
                if record["registered"]:
                    if len(record["registered"]) == 1:
                        registered = record["registered"][0]
                    else:
                        registered = record["registered"][-1]

                accepted = None
                if record["accepted"]:
                    if len(record["accepted"]) == 1:
                        accepted = record["accepted"][0]
                    else:
                        accepted = record["accepted"][-1]

                receipt = None
                if record["receipt"]:
                    if len(record["receipt"]) == 1:
                        receipt = record["receipt"][0]
                    else:
                        receipt = record["receipt"][-1]

                registered_interest = self._create_interest(record["interest"])
                registered_interest.set_interest_details()

                funding_relationship = self._create_relationship(
                    self.current_detail["mp"],
                    record["interest"]
                )

                category.link_relationship(funding_relationship)
                funding_relationship.link_contributor(registered_interest)

                meta = {
                    "recorded date": self.current_detail["recorded_date"],
                    "source_url": self.current_detail["source_url"],
                    "source_linked_from": self.current_detail["source_linked_from"],
                    "source_fetched": str(self.current_detail["source_fetched"]),
                    "contributor": record["interest"],
                    "recipient": self.current_detail["mp"],
                    "nature": record["nature"],
                    "receipt": receipt,
                    "accepted": accepted,
                    "donor_status": record["donor_status"],
                }

                if record["remuneration"] and len(record["remuneration"]) > 0:
                    for entry in record["remuneration"]:
                        amount = entry
                        int_amount = self.convert_to_number(amount)
                        summary = u"{} - {} - {} - {} - {}".format(
                            record["interest"],
                            self.current_detail["category"],
                            self.current_detail["mp"],
                            amount,
                            registered
                        )

                        interest_detail = InterestDetail(summary)
                        interest_detail.create()
                        interest_detail.set_interest_details({"amount": int_amount})
                        interest_detail.set_interest_details(meta)
                        # interest_detail.update_raw_record(record["raw_record"])

                        funding_relationship.link_interest_detail(interest_detail)

                        if registered:
                            interest_detail.set_interest_details({"registered": registered})
                            interest_detail.set_registered_date(registered)
                        self._logger.debug(summary)
                else:
                    summary = u"{} - {} - {} - {}".format(
                        record["interest"],
                        self.current_detail["category"],
                        self.current_detail["mp"],
                        registered
                    )
                    interest_detail = InterestDetail(summary)
                    interest_detail.create()
                    interest_detail.set_interest_details(meta)
                    # interest_detail.update_raw_record(record["raw_record"])

                    funding_relationship.link_interest_detail(interest_detail)

                    if registered:
                        interest_detail.set_interest_details({"registered": registered})
                        interest_detail.set_registered_date(registered)

    def _create_graph(self, category, records):
        if records:
            for record in records:
                if record["interest"] and record["interest"] != "None":
                    self.current_detail["contributor"] = record["interest"]

                    funding_relationship = self._create_relationship(
                        self.current_detail["mp"],
                        record["interest"]
                    )

                    new_interest = self._create_interest(record["interest"])
                    new_interest.set_interest_details()

                    meta = {
                        "recorded date": self.current_detail["recorded_date"],
                        "source_url": self.current_detail["source_url"],
                        "source_linked_from": self.current_detail["source_linked_from"],
                        "source_fetched": str(self.current_detail["source_fetched"]),
                        "contributor": record["interest"],
                        "recipient": self.current_detail["mp"],
                        # "raw_record": record["raw_record"]
                    }

                    category.link_relationship(funding_relationship)
                    funding_relationship.link_contributor(new_interest)

                    if self._is_remuneration(record):
                        for payment in record["remuneration"]:
                            self._create_remuneration(funding_relationship, payment, meta)

                    if "registered" in record and record["registered"]:
                        for entry in record["registered"]:
                            funding_relationship.set_registered_date(entry)

                    for detail in self.extra_details:
                        if detail in record:
                            funding_relationship.vertex[detail] = record[detail]
                    funding_relationship.vertex.push()
                else:
                    self.current_detail["contributor"] = "Unknown"
                    self._logger.debug("** NO CONTRIBUTOR ** ")
                    self._logger.debug(self.current_detail)
                    self._logger.debug("** NO CONTRIBUTOR ** ")

    def _create_category(self, name, category):
        props = {"mp": name, "category": category}
        category_name = u"{} - {}".format(name, category)
        new_category = InterestCategory(category_name)
        if not new_category.exists:
            new_category.create()
        new_category.update_category_details(props)
        return new_category

    def _create_relationship(self, name, donor):
        props = {"recipient": name, "contributor": donor}
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
        #entry.update_raw_record(raw_record)
        return entry

    def _create_remuneration(self, relationship, payment_details, meta):
        context = u"{} - {} - {}".format(
            self.current_detail["contributor"],
            self.current_detail["category"],
            self.current_detail["mp"]
        )
        if isinstance(payment_details, dict):
            amount = payment_details["amount"]
            int_amount = self.convert_to_number(amount)

            summary = u"{} - £{} - {}".format(
                context, amount, payment_details["received"]
            )
            payment = InterestDetail(summary)
            payment.create()

            payment.set_interest_details(payment_details)
            payment.set_interest_details({"amount": int_amount})
            payment.set_interest_details(meta)
            relationship.link_interest_detail(payment)

            if payment_details["received"] != u"Unknown":
                payment.set_received_date(payment_details["received"])
            if payment_details["registered"] != u"Unknown":
                payment.set_received_date(payment_details["registered"])

        elif isinstance(payment_details, list):
            for payment in payment_details:
                summary = u"{} - £{} - {}".format(
                    context, payment, u"Unknown"
                )
                int_amount = self.convert_to_number(payment)
                payment = InterestDetail(summary)
                payment.create()

                relationship.link_interest_detail(payment)
                payment.set_interest_details({"amount": int_amount})
                payment.set_interest_details(meta)
        else:
            summary = u"{} - £{} - {}".format(
                context, payment_details, u"Unknown"
            )
            int_amount = self.convert_to_number(payment_details)
            payment = InterestDetail(summary)
            payment.create()

            relationship.link_interest_detail(payment)
            payment.set_interest_details({"amount": int_amount})
            payment.set_interest_details(meta)

    def _print_out(self, key, value):
        self._logger.debug("  %-25s%-25s" % (key, value))

    @staticmethod
    def _is_remuneration(record):
        result = False
        if "remuneration" in record:
            if record["remuneration"] and len(record["remuneration"]) > 0:
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
