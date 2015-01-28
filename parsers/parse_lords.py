from utils import mongo
from utils import entity_resolver


class LordsParser():
    def run(self):
        self._cache = mongo.MongoInterface()
        self._cache_data = self._cache.db.scraped_lords_info
        self._parsed_data = self._cache.db.parsed_lords_info
        self.resolver = entity_resolver.MasterEntitiesResolver()
        self._all_lords = []

        self._all_lords = list(self._cache_data.find().sort("full_name", 1))
        for doc in self._all_lords:
            self._parse(doc)

    def _parse(self, node):
        found = self.resolver.find_lord(node["full_name"])
        party = self.resolver.find_party(node["party"])
        print "\n.................."
        print found, "x", node["number_of_terms"]
        if node["full_name"] != found:
            print "*** also known as:", node["full_name"]
            node["also_known_as"] = found
        if node["party"] != party:
            print node["party"], "%", party
            node["party"] = party
        print ".................."
        self._parsed_data.save(node)
        #print node["twfy_id"]
