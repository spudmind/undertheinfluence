# -*- coding: utf-8 -*-
import logging
from utils import mongo
from utils import config


class MasterEntitiesParser:
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.mapped_mps = config.mapped_mps
        self._titles = [
            "Earl", "Bishop", "Archbishop", "Duke", "Marquess", "Countess"
        ]

    def create_mps(self):
        _all_mps = self.db.fetch_all('scraped_mp_info', paged=False)
        self._print_out("Original", "*Updated")
        for mp in _all_mps:
            name = None
            for incorrect, correct in self.mapped_mps:
                if incorrect in mp["full_name"]:
                    name = correct
            if not name:
                name = mp["full_name"]
            self._print_out(mp["full_name"], name)
            self.db.save('master_mps', {"name": name})

    def create_lords(self):
        _all_lords = self.db.fetch_all('scraped_lords_info', paged=False)
        for doc in _all_lords:
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
                    self._logger.debug(full_name)
                    self.db.save('master_lords', {"name": full_name})
                else:
                    self._logger.debug("%s -> %s" % (title_last, full_name))
                    self.db.save('master_lords', {"name": title_last})
                    self.db.save('master_lords', {"name": full_name})
            else:
                self._logger.debug(full_name)
                self.db.save('master_lords', {"name": full_name})

    def _print_out(self, key, value):
        self._logger.debug("  %-30s%-20s" % (key, value))
