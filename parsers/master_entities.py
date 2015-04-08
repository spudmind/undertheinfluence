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
        self.db.drop("master_mps")
        _all_mps = self.db.fetch_all('mps_scrape', paged=False)
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
        self.db.drop("master_lords")
        _all_lords = self.db.fetch_all('lords_scrape', paged=False)
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

    def create_positions(self):
        self.db.drop("master_positions")
        additional = [
            "Secretary of State",
            "Secretary of State for Business, Innovation & Skills and President of the Board of Trade",
            "Minister of State (Business and Enterprise)",
            "Minister of State (Further Education, Skills and Lifelong Learning)",
            "Minister of State (Trade and Investment)",
            "Minister for Sport and Tourism",
            "Minister for Tourism and Heritage",
            "Minister for Sport and the Olympics",
            "Minister for Culture, Communications and Creative Industries",
            "Minister for Defence Equipment, Support and Technology"
        ]
        _all_mps = self.db.fetch_all('mps_scrape', paged=False)
        all_positions = []
        for mp in _all_mps:
            if "terms" in mp:
                for term in mp["terms"]:
                    if "offices_held" in term:
                        positions = self._get_offices(term["offices_held"])
                        all_positions = all_positions + positions
        all_positions = list(set(all_positions))
        for position in all_positions:
            self._print_out("position", position)
            self.db.save('master_positions', {"position": position})
        for position in additional:
            self._print_out("position", position)
            self.db.save('master_positions', {"position": position})

    def _get_offices(self, offices):
        positions = []
        if len(offices) > 1 and offices != "none":
            for office in offices:
                if "position" in office and office["position"]:
                    positions.append(office["position"])
        else:
            if not offices == "none":
                if "position" in offices[0] and offices[0]["position"]:
                    positions.append(offices[0]["position"])
        return positions

    def _print_out(self, key, value):
        self._logger.debug("  %-30s%-20s" % (key, value))
