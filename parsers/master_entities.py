from utils import mongo
from utils import entity_resolver


class MasterEntitiesParser:
    def __init__(self, bootstrap=False):
        self.boot = bootstrap
        self._resolver = entity_resolver.MasterEntitiesResolver()
        self._cache = mongo.MongoInterface()
        self.scraped_mps = self._cache.db.scraped_mp_info
        self.scraped_lords = self._cache.db.scraped_lords_info
        self.master_mps = self._cache.db.master_mps
        self.master_lords = self._cache.db.master_lords
        self._all_mps = []
        self._all_lords = []
        self._titles = [
            "Earl", "Bishop", "Archbishop", "Duke", "Marquess", "Countess"
        ]

    def create_mps(self):
        self._all_mps = list(self.scraped_mps.find())
        self._print_out("Original", "*Updated")
        for mp in self._all_mps:
            name = self._resolver.find_mp(mp["full_name"])
            self._print_out(mp["full_name"], name)
            self.master_mps.save({"name": name})

    def create_lords(self):
        self._all_lords = list(self.scraped_lords.find().sort("full_name", 1))
        for doc in self._all_lords:
            full_name = doc["full_name"]
            title = doc["title"]
            first = doc["first_name"]
            last = doc["last_name"]
            title_last_first = u"{} {}, {}".format(title, last, first)
            title_first_last = u"{} {} {}".format(title, first, last)
            title_last = u"{} {}".format(title, last)
            if full_name != title_last:
                if doc["title"] in self._titles:
                    #pass
                    print full_name
                    self.master_lords.save({"name": full_name})
                else:
                    print title_last, "->", full_name
                    self.master_lords.save({"name": title_last})
                    self.master_lords.save({"name": full_name})
            else:
                #pass
                print full_name
                self.master_lords.save({"name": full_name})


    @staticmethod
    def _print_out(key, value):
        print "  %-30s%-20s" % (key, value)
