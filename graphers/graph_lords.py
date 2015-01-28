from utils import mongo
from data_models import models


class GraphLords():
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.parsed_lords_info
        self.data_models = models
        self.full_update = True
        self.all_lords = []

    def run(self):
        self.all_lords = list(self.cache_data.find())
        for doc in self.all_lords:
            self._import(doc)

    def _import(self, node):
        lord = self.graph_lord(node)
        if self.full_update:
            if "terms" in node:
                self.import_terms(lord, node["terms"])

    def graph_lord(self, node):
        print "\n.................."
        print node["full_name"], "x", node["number_of_terms"]
        if "also_known_as" in node:
            print "AKA:", node["full_name"]
        print node["party"]
        print ".................."
        #print node["twfy_id"]
        return self._create_lord(node)

    def _create_lord(self, lord):
        new_lord = self.data_models.Lord(lord["full_name"])
        lord_details = {
            "first_name": lord["first_name"],
            "last_name": lord["last_name"],
            "party": lord["party"],
            "title": lord["title"],
            "twfy_id": lord["twfy_id"],
            "number_of_terms": lord["number_of_terms"]
        }
        if not new_lord.exists:
            new_lord.create()
        new_lord.update_lord_details(lord_details)
        new_lord.link_party(lord["party"])
        return new_lord

    def import_terms(self, lord, terms):
        for term in terms:
            print term["constituency"], "-", term["party"]
            print term["entered_house"], "to", term["left_house"]
            print term["left_reason"]
            new_term = self._create_term(term)
            lord.link_peerage(new_term)
            print "-"

    def _create_term(self, term):
        session = u"{0} {1} {2} to {3}".format(
            term["constituency"],
            term["party"],
            term["entered_house"],
            term["left_house"]
        )
        new_term = self.data_models.TermInParliament(session)
        if not new_term.exists:
            new_term.create()
        label = "Peerage"
        term = {
            "party": term["party"],
            "constituency": term['constituency'],
            "left_house": term["left_house"],
            "entered_house": term["entered_house"],
            "left_reason": term["left_reason"],
            "type": "Peerage",
        }
        new_term.update_details(labels=label, properties=term)
        if term['constituency']:
            #print "-->", term['constituency']
            new_constituency = self.data_models.Constituency(term['constituency'])
            new_constituency.create()
            new_term.link_constituency(new_constituency)
        return new_term

    @staticmethod
    def _print_out(key, value):
        print "  %-20s%-15s" % (key, value)