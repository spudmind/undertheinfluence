from data_interfaces import hansard
from utils import mongo
from fuzzywuzzy import process
import requests
import os


class MPsInfoScaper():
    current_path = os.path.dirname(os.path.abspath(__file__))
    ALL_PARTIES_API = 'http://www.theguardian.com/politics/api/party/all/json'
    VOTE_MATRIX = current_path + '/data/votematrix-2010.csv'
    TEST = None

    def __init__(self):
        print "Importing MPs"
        self.fuzzy_match = process
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.scraped_mp_info
        self.requests = requests
        self.hansard = hansard.TWFYHansard()
        self.mps = self.hansard.get_mps()
        self.all_mps = None

    def run(self):
        self._get_twfy_data()
        self._get_guardian_data()
        self._get_publicwhip_data()

    def _get_twfy_data(self):
        print "Getting Mps from TWFY"
        print self.mps
        for mp in self.mps:
            self._print_out("MP", mp["name"])
            self._print_out("Party", mp["party"])
            self._print_out("person_id", mp["person_id"])
            node = {
                "full_name": mp["name"],
                "twfy_id": mp["person_id"],
                "publicwhip_id": None,
                "party": mp["party"],
                "guardian_url": None,
                "publicwhip_url": None,
                "guardian_image": None
            }
            print "\n"
            details = self.hansard.get_mp_details(mp["person_id"])
            if details:
                node["first_name"] = details[0]["first_name"]
                node["last_name"] = details[0]["last_name"]
                node["number_of_terms"] = len(details)
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
            self._report(node)
            self.cache_data.save(node)
            print "---"

    def _get_guardian_data(self):
        print "Updating Guardian data"
        self.all_mps = [
            doc["full_name"] for doc in self.cache_data.find()
        ]
        for person in self._iterate_guardian_api():
            url = person["aristotle-url"]
            cached = self._find_cached_mp(person["name"])
            self._update_cached_mp(cached["_id"], "guardian_url", url)
            if "image" in person:
                self._update_cached_mp(
                    cached["_id"], "guardian_image", person["image"]
                )
            self._print_out(cached["full_name"], url)

    def _get_publicwhip_data(self):
        with open(MpInfoScaper.VOTE_MATRIX) as fin:
            rows = (line.split('\t') for line in fin)
            for row in rows:
                name, id = u'{0} {1}'.format(row[1], row[2]), row[0]
                url = u"http://publicwhip.com/mp.php?mpid={0}".format(id)
                result = self._find_cached_mp(name)
                self._update_cached_mp(result["_id"], "publicwhip_id", id)
                self._update_cached_mp(result["_id"], "publicwhip_url", url)
                self._print_out(name, url)

    def _iterate_guardian_api(self):
        r = self.requests.get(MpInfoScaper.ALL_PARTIES_API)
        parties = r.json()["parties"]
        for party in parties:
            party_uri = party["json-url"]
            r = self.requests.get(party_uri)
            if not r.status_code == 404:
                mps = r.json()["party"]["mps"]
                for mp in mps:
                    mp_uri = mp["json-url"]
                    r = self.requests.get(mp_uri)
                    if not r.status_code == 404:
                        person = r.json()["person"]
                        yield person

    def _find_cached_mp(self, search):
        if self.all_mps:
            cand = self.fuzzy_match.extractOne(search, self.all_mps)
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
        print "  %-25s%-15s" % (key, value)
