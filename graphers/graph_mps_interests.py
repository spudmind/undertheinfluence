# -*- coding: utf-8 -*-
from utils import mongo
from data_models import models


class GraphMPsInterests():
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.parsed_mps_interests
        self.data_models = models
        self.all_mps = []
        self.extra_details = [
            "donor_status",
            "purpose",
            "visit_dates",
            "receipt",
            "accepted",
            "nature"
        ]

    def run(self):
        self.all_mps = list(self.cache_data.find())
        for doc in self.all_mps:
            self._graph_interests(doc)

    def _graph_interests(self, node):
        self.current_detail = {}
        print "\n.................."
        print node["mp"]
        print ".................."
        #print "\n", node, "\n"
        mp = self._find_mp(node["mp"])
        self.current_detail["mp"] = node["mp"]
        self._parse_categories(mp, node["interests"])

    def _find_mp(self, mp):
        new_mp = self.data_models.MemberOfParliament(mp)
        if not new_mp.exists:
            print mp, "*not found*"
            new_mp.create()
        return new_mp

    def _parse_categories(self, mp, categories):
        for category in categories:
            category_name = category["category_name"]
            self.current_detail["category"] = category_name
            new_category = self._create_category(mp.name, category_name)
            mp.link_interest_category(new_category)
            if category_name == "Directorships":
                #continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Remunerated directorships":
                #continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Remunerated employment, office, profession etc":  # done
                #continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Remunerated employment, office, profession, etc_":  # done
                #continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Clients":
                #continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Land and Property":
                #continue
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Shareholdings":
                #continue
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Registrable shareholdings":
                #continue
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Sponsorships":
                #continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Sponsorship or financial or material support":
                #continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Overseas visits":
                #continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Gifts, benefits and hospitality (UK)":
                #continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Gifts, benefits and hospitality (UK)":
                #continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Miscellaneous":
                #continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            print "*"

    def _create_graph(self, category, records):
        if records:
            for record in records:
                self._print_out("interest", record["interest"])
                if record["interest"] and record["interest"] != "None":
                    self.current_detail["contributor"] = record["interest"]
                    funding_relationship = self._create_relationship(
                        self.current_detail["mp"],
                        record["interest"]
                    )
                    new_interest = self._create_interest(record["interest"])
                    new_interest.update_interest_details()
                    category.link_relationship(funding_relationship)
                    funding_relationship.link_donor(new_interest)
                    funding_relationship.update_raw_record(record["raw_record"])
                    if self._is_remuneration(record):
                        for payment in record["remuneration"]:
                            self._create_remuneration(funding_relationship, payment)
                    if "registered" in record and record["registered"]:
                        for entry in record["registered"]:
                            funding_relationship.set_registered_date(entry)
                    for detail in self.extra_details:
                        if detail in record:
                            funding_relationship.vertex[detail] = record[detail]
                    funding_relationship.vertex.push()
                else:
                    self.current_detail["contributor"] = "Unknown"
                    print "** NO CONTRIBUTOR ** "
                    print self.current_detail
                    print "** NO CONTRIBUTOR ** "
                print "-\n"

    def _create_category(self, name, category):
        props = {"mp": name, "category": category}
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
        new_relationship.update_category_details(props)
        return new_relationship

    def _create_interest(self, interest):
        if isinstance(interest, list):
            interest = interest[0]
        entry = self.data_models.RegisteredInterest(interest)
        if not entry.exists:
            entry.create()
        #entry.update_raw_record(raw_data)
        return entry

    def _create_remuneration(self, relationship, payment_details):
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
            payment = self.data_models.Remuneration(summary)
            payment.create()
            payment.update_details(payment_details)
            payment.update_details({"amount": int_amount})
            relationship.link_payment(payment)
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
                payment = self.data_models.Remuneration(summary)
                payment.create()
                relationship.link_payment(payment)
                payment.update_details({"amount": int_amount})
        else:
            summary = u"{} - £{} - {}".format(
                context, payment_details, u"Unknown"
            )
            int_amount = self.convert_to_number(payment_details)
            payment = self.data_models.Remuneration(summary)
            payment.create()
            relationship.link_payment(payment)
            payment.update_details({"amount": int_amount})

    @staticmethod
    def _print_out(key, value):
        print "  %-25s%-25s" % (key, value)

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
