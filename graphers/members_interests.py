from utils import mongo
from data_models import models


class GraphMembersInterests():
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.parsed_mps_interests
        self.data_models = models
        self.all_mps = []

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
            #new_mp.create()
            print mp, "*not found*"
        return new_mp

    def _parse_categories(self, mp, categories):
        for category in categories:
            if category["category_name"] == "Directorships":
                self.current_detail["category"] = category["category_name"]
                print category["category_name"]
                new_category = self._create_category(
                    mp.name,
                    category["category_name"]
                )
                mp.link_interest_category(new_category)
                self._graph_list_record(new_category, category["category_records"])
                print "*"

    def _graph_list_record(self, category, records):
        for record in records:
            self._print_out("interest", record["interest"])
            self._print_out("renumeration", record["renumeration"])
            #self._print_out("raw_record", record["raw_record"])
            new_interest = self._create_interest(record["raw_record"])
            if not new_interest.exists:
                new_interest.create()
            category.link_interest(new_interest)
            if record["interest"] and record["interest"] != "None":
                self.current_detail["contributor"] = record["interest"]
                new_contributor = self._create_contributor(record["interest"])
                new_interest.link_contributor(new_contributor)
            if len(record["renumeration"]) > 0:
                for payment in record["renumeration"]:
                    #print list(self.current_detail.values())
                    new_payment = self._create_remuneration(payment)
                    new_interest.link_payment(new_payment)
            print "-\n"

    def _create_category(self, name, category):
        print category
        props = {"mp": name, "category": category}
        category_name = u"{} - {}".format(name, category)
        new_category = self.data_models.InterestCategory(category_name)
        if not new_category.exists:
            new_category.create()
        new_category.update_category_details(props)
        return new_category

    def _create_interest(self, interest):
        entry = self.data_models.RegisteredInterest(interest)
        if not entry.exists:
            entry.create()
        return entry

    def _create_contributor(self, name):
        entry = self.data_models.Contributor(name)
        if not entry.exists:
                entry.create()
        return entry

    def _create_remuneration(self, payment_details):
        amount = payment_details["amount"]
        summary = u"{} - {} - {} - {}".format(
            self.current_detail["contributor"],
            self.current_detail["category"],
            self.current_detail["mp"],
            amount
        )
        payment = self.data_models.Remuneration(summary)
        if not payment.exists:
            payment.create()
        payment.update_details(payment_details)
        if payment_details["recieved"] != u"Unknown":
            payment.set_recieved_date(payment_details["recieved"])
        if payment_details["registered"] != u"Unknown":
            payment.set_recieved_date(payment_details["registered"])
        return payment



    @staticmethod
    def _print_out(key, value):
        print "  %-20s%-15s" % (key, value)