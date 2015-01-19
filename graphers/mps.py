from utils import mongo
from data_models import models


class GraphMPs():
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.parsed_mp_info
        self.data_models = models
        self.full_update = True
        self.all_mps = []

    def run(self):
        self.all_mps = list(self.cache_data.find())
        for doc in self.all_mps:
            self._import(doc)

    def _import(self, node):
        mp = self.graph_mp(node)
        if self.full_update:
            if "terms" in node:
                self.import_terms(mp, node["terms"])

    def graph_mp(self, node):
        print "\n.................."
        print node["full_name"], "x", node["number_of_terms"]
        if "also_known_as" in node:
            print "AKA:", node["full_name"]
        print node["party"]
        print ".................."
        #print node["twfy_id"]
        return self._create_mp(node)

    def _create_mp(self, mp):
        new_mp = self.data_models.MemberOfParliament(mp["full_name"])
        mp_details = {
            "first_name": mp["first_name"],
            "last_name": mp["last_name"],
            "party": mp["party"],
            "twfy_id": mp["twfy_id"],
            "number_of_terms": mp["number_of_terms"]
        }
        if "guardian_url" in mp:
            mp_details["guardian_url"] = mp["guardian_url"]
        if "guardian_image" in mp:
            mp_details["guardian_image"] = mp["guardian_image"]
        if "publicwhip_url" in mp:
            mp_details["publicwhip_url"] = mp["publicwhip_url"]
            mp_details["publicwhip_id"] = mp["publicwhip_id"]
        if not new_mp.exists:
            new_mp.create()
        new_mp.update_mp_details(mp_details)
        new_mp.link_party(mp["party"])
        if "also_known_as" in mp:
            aka = self.create_alternate(mp["also_known_as"], mp_details)
            new_mp.link_alternate(aka)
        return new_mp

    def create_alternate(self, also_known_as, details):
        aka = self.data_models.MemberOfParliament(also_known_as)
        if not aka.exists:
            aka.create()
        aka.update_mp_details(details)
        return aka

    def import_terms(self, mp, terms):
        for term in terms:
            print term["constituency"], term["party"]
            print term["entered_house"], "to", term["left_house"]
            print term["left_reason"]
            new_term = self._create_term(term)
            mp.link_elected_term(new_term)
            if "offices_held" in term:
                self._create_offices(new_term, term["offices_held"])
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
        term = {
            "party": term["party"],
            "constituency": term['constituency'],
            "left_house": term["left_house"],
            "entered_house": term["entered_house"],
            "left_reason": term["left_reason"]
        }
        new_term.update_details(term)
        new_term.link_constituency(term['constituency'])
        return new_term

    def _create_offices(self, term, offices):
        print "*"
        if len(offices) > 1 and offices != "none":
            for office in offices:
                if "department" in office:
                    self._create_office(
                        term, "department", office["department"]
                    )
                if "position" in office:
                    self._create_office(
                        term, "position", office["position"]
                    )
        else:
            if not offices == "none":
                if "department" in offices[0]:
                    self._create_office(
                        term, "department", offices[0]["department"]
                    )
                if "position" in offices[0]:
                    self._create_office(
                        term, "position", offices[0]["position"]
                    )

    def _create_office(self, term, create_as, office):
        print office
        new_office = None
        if create_as == "department":
            new_office = self.data_models.GovernmentOffice(office)
            new_office.create()
            new_office.is_department()
        elif create_as == "position":
            new_office = self.data_models.GovernmentOffice(office)
            new_office.create()
            new_office.is_position()
        if new_office.exists:
            term.link_position(new_office)

    @staticmethod
    def _print_out(key, value):
        print "  %-20s%-15s" % (key, value)