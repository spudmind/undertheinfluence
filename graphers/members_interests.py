# -*- coding: utf-8 -*-
from utils import mongo
from data_models import models


class GraphMembersInterests():
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.parsed_mps_interests
        self.data_models = models
        self.all_mps = []
        self.extra_details = [
            "donor_status",
            "purpose",
            "vist_dates",
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
        if not mp.exists:
            mp.create()
        self.current_detail["mp"] = node["mp"]
        self._parse_categories(mp, node["interests"])

    def _find_mp(self, mp):
        new_mp = self.data_models.MemberOfParliament(mp)
        if not new_mp.exists:
            #new_mp.create()
            print mp, "*not found*"
        return new_mp

    def _parse_categories(self, mp, categories):
        for category in categories:
            category_name = category["category_name"]
            self.current_detail["category"] = category_name
            new_category = self._create_category(mp.name, category_name)
            mp.link_interest_category(new_category)
            if category_name == "Directorships":
                continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Remunerated directorships":
                continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Remunerated employment, office, profession etc":  # done
                continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Remunerated employment, office, profession, etc_":  # done
                continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Clients":
                continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Land and Property":
                continue
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Shareholdings":
                continue
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Registrable shareholdings":
                continue
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Sponsorships":
                continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Sponsorship or financial or material support":
                continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Overseas visits":
                continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Gifts, benefits and hospitality (UK)":
                continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Gifts, benefits and hospitality (UK)":
                continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            elif category_name == "Miscellaneous":
                continue
                print category_name
                self._create_graph(new_category, category["category_records"])
            print "*"

    def _create_graph(self, category, records):
        for record in records:
            self._print_out("interest", record["interest"])
            if record["interest"] and record["interest"] != "None":
                self.current_detail["contributor"] = record["interest"]
                new_interest = self._create_interest(
                    record["interest"],
                    record["raw_record"]
                )
                category.link_interest(new_interest)
                if "renumeration" in record and len(record["renumeration"]) > 0:
                    for payment in record["renumeration"]:
                        new_payment = self._create_remuneration(payment)
                        new_interest.link_payment(new_payment)
                if "registered" in record and record["registered"]:
                    for entry in record["registered"]:
                        new_interest.set_registered_date(entry)
                for detail in self.extra_details:
                    if detail in record:
                        new_interest.vertex[detail] = detail
                new_interest.vertex.push()
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

    def _create_interest(self, interest, raw_data):
        summary = u"{} - {} - {}".format(
            self.current_detail["category"],
            self.current_detail["contributor"],
            self.current_detail["mp"]
        )
        props = {
            "interest_type": self.current_detail["category"],
            "summary": summary
        }
        entry = self.data_models.RegisteredInterest(interest)
        if not entry.exists:
            entry.create()
        entry.update_interest_details(props)
        entry.update_raw_record(raw_data)
        return entry

    def _create_contributor(self, name):
        entry = self.data_models.Contributor(name)
        if not entry.exists:
            entry.create()
        return entry

    def _create_remuneration(self, payment_details):
        context = u"{} - {} - {}".format(
            self.current_detail["contributor"],
            self.current_detail["category"],
            self.current_detail["mp"]
        )
        if isinstance(payment_details, dict):
            amount = payment_details["amount"]
            summary = u"{} - £{} - {}".format(
                context, amount, payment_details["recieved"]
            )
            payment = self.data_models.Remuneration(summary)
            payment.create()
            payment.update_details(payment_details)
            if payment_details["recieved"] != u"Unknown":
                payment.set_received_date(payment_details["recieved"])
            if payment_details["registered"] != u"Unknown":
                payment.set_received_date(payment_details["registered"])
            return payment
        elif isinstance(payment_details, list):
            for payment in payment_details:
                summary = u"{} - £{} - {}".format(
                    context, payment, u"Unknown"
                )
                payment = self.data_models.Remuneration(summary)
                payment.create()


    @staticmethod
    def _print_out(key, value):
        print "  %-25s%-25s" % (key, value)
