from utils import mongo
from utils import entity_resolver


class MasterEntitiesParser:
    def __init__(self, bootstrap=False):
        self.boot = bootstrap
        self.resolver = entity_resolver.MasterEntitiesResolver()
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.scraped_mp_info
        self.master_data = self.cache.db.master_mps
        self.all_mps = []

    def _create(self):
        self.all_mps = list(self.cache_data.find())
        self._print_out("Original", "*Updated")
        for mp in self.all_mps:
            name = self.resolver.find_mp(mp["full_name"])
            self._print_out(mp["full_name"], name)
            self.master_data.save({"name": name})

    @staticmethod
    def _print_out(key, value):
        print "  %-30s%-20s" % (key, value)
