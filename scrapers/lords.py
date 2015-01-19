from data_interfaces import hansard
from utils import mongo
from fuzzywuzzy import process
import requests
import os


class LordsInfoScaper():
    current_path = os.path.dirname(os.path.abspath(__file__))
    ALL_PARTIES_API = 'http://www.theguardian.com/politics/api/party/all/json'
    VOTE_MATRIX = current_path + '/data/votematrix-2010.csv'
    TEST = None

    def __init__(self):
        print "Importing Lords"
        self.fuzzy_match = process
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.scraped_lords_info
        self.requests = requests
        self.hansard = hansard.TWFYHansard()
        self.lords = self.hansard.get_lords()
        self.all_lords = None

    def run(self):
        #self._get_twfy_data()
        self._get_guardian_data()
        #self._get_publicwhip_data()

    def _get_twfy_data(self):
        print "Getting Lords from TWFY"
        for lord in self.lords:
            self._print_out("Lord", lord["name"])
            self._print_out("Party", lord["party"])
            self._print_out("person_id", lord["person_id"])
            node = {
                "full_name": lord["name"],
                "twfy_id": lord["person_id"],
                "publicwhip_id": None,
                "party": lord["party"],
                "guardian_url": None,
                "publicwhip_url": None,
                "guardian_image": None
            }
            #print "\n"
            details = self.hansard.get_lord_details(lord["person_id"])
            if details:
                node["first_name"] = details[0]["first_name"]
                node["last_name"] = details[0]["last_name"]
                node["title"] = details[0]["title"]
                node["number_of_terms"] = len(details)
                self._print_out("first_name", node["first_name"])
                self._print_out("last_name", node["last_name"])
            terms = []
            for entry in details:
                term = {
                    "party": entry["party"],
                    "constituency": entry['constituency'],
                    "left_house": entry["left_house"],
                    "entered_house": entry["entered_house"],
                    "left_reason": entry["left_reason"]
                }
                if "office" in entry:
                    offices = self._get_office(entry["office"])
                    if len(offices) > 0:
                        term["offices_held"] = offices
                terms.append(term)
            node["terms"] = terms
            #self._report(node)
            self.cache_data.save(node)
            print "\n\n---"

    def _get_guardian_data(self):
        print "Updating Guardian data"
        self.all_lords = [
            #doc["full_name"] for doc in self.cache_data.find()
            u"{} {} {}".format(doc["title"], doc["first_name"], doc["last_name"])
            for doc in self.cache_data.find()
        ]
        for person in self._iterate_guardian_api():
            url = person["aristotle-url"]
            cached = self._find_cached_lord(person["name"])
            if cached:
                self._update_cached_mp(cached["_id"], "guardian_url", url)
                if "image" in person:
                    self._update_cached_mp(
                        cached["_id"], "guardian_image", person["image"]
                    )
                self._print_out(cached["full_name"], url)

    def _get_publicwhip_data(self):
        with open(LordsInfoScaper.VOTE_MATRIX) as fin:
            rows = (line.split('\t') for line in fin)
            for row in rows:
                name, id = u'{0} {1}'.format(row[1], row[2]), row[0]
                url = u"http://publicwhip.com/mp.php?mpid={0}".format(id)
                result = self._find_cached_lord(name)
                self._update_cached_mp(result["_id"], "publicwhip_id", id)
                self._update_cached_mp(result["_id"], "publicwhip_url", url)
                self._print_out(name, url)

    def _iterate_guardian_api(self):
        r = self.requests.get(LordsInfoScaper.ALL_PARTIES_API)
        parties = r.json()["parties"]
        for party in parties:
            party_uri = party["json-url"]
            r = self.requests.get(party_uri)
            if not r.status_code == 404:
                people = r.json()["party"]["mps"]
                for person in people:
                    person_uri = person["json-url"]
                    r = self.requests.get(person_uri)
                    if not r.status_code == 404:
                        yield r.json()["person"]

    def _find_cached_lord(self, search):
        if self.all_lords:
            cand = self.fuzzy_match.extractOne(search, self.all_lords)
            print search, cand
            name = cand[0]
        else:
            name = search
        result = self.cache_data.find({"full_name": name}).limit(1)
        try:
            return result[0]
        except IndexError:
            return None

    def _update_cached_mp(self, id, key, value):
        self.cache_data.update({"_id": id}, {"$set": {key: value}})

    def _get_office(self, positions):
        offices = []
        if len(positions) > 1:
            for position in positions:
                office = {}
                if position["dept"]:
                    office = {"department": position["dept"]}
                if position["position"]:
                    office = {"position": position["position"]}
                offices.append(office)
        else:
            office = {}
            if positions[0]["dept"]:
                office = {"department": positions[0]["dept"]}
            if positions[0]["position"]:
                office = {"position": positions[0]["position"]}
            offices.append(office)
        if len(offices) == 0:
            return None
        else:
            return offices

    def _report(self, node):
        for x in node:
                if x == "terms":
                    for term in node["terms"]:
                        print "-"
                        for y in term:
                            if y == "offices_held":
                                offices = term["offices_held"]
                                if len(offices) > 1 and offices != "none":
                                    for office in offices:
                                        for z in office:
                                            self._print_out(z, office[z])
                                else:
                                    if not offices == "none":
                                        for z in offices[0]:
                                            self._print_out(z, offices[0][z])
                            else:
                                self._print_out(y, term[y])
                else:
                    self._print_out(x, node[x])

    @staticmethod
    def _print_out(key, value):
        print "  %-35s%-25s" % (key, value)