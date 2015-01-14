from utils import mongo
from utils import entity_resolver


class MpsParser():
    def __init__(self):
        self._cache = mongo.MongoInterface()
        self._cache_data = self._cache.db.scraped_mp_info
        self._parsed_data = self._cache.db.parsed_mp_info
        self.resolver = entity_resolver.MasterEntitiesResolver()
        self._all_mps = []

    def run(self):
        self._all_mps = list(self._cache_data.find())
        for doc in self._all_mps:
            self._parse(doc)

    def _parse(self, node):
        found = self.resolver.find_mp(node["full_name"])
        party = self.resolver.find_party(node["party"])
        print "\n.................."
        #print node
        print found, "x", node["number_of_terms"]
        if node["full_name"] != found:
            print "*** also known as:", node["full_name"]
            node["also_known_as"] = found
        if node["party"] != party:
            print node["party"], "%", party
            node["party"] = party
        #print node["party"]
        #print node["constituency"]
        print ".................."
        self._parsed_data.save(node)
        #print node["twfy_id"]
