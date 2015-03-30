# -*- coding: utf-8 -*-
import logging
from utils import mongo
from utils import entity_resolver


class ParseMps():
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.resolver = entity_resolver.MasterEntitiesResolver()
        self.PREFIX = "mps"
        if kwargs["refreshdb"]:
            self.db.drop("%s_parse" % self.PREFIX)

    def run(self):
        #self._all_mps = list(self._cache_data.find())
        _all_mps = self.db.fetch_all("%s_scrape" % self.PREFIX, paged=False)
        for doc in _all_mps:
            self._parse(doc)

    def _parse(self, node):
        found = self.resolver.find_mp(node["full_name"])
        party = self.resolver.find_party(node["party"])
        self._logger.debug("\n..................")
        self._logger.debug("%s x %s" % (found, node["number_of_terms"]))
        if node["full_name"] != found:
            self._logger.debug("*** also known as: %s" % node["full_name"])
            node["also_known_as"] = node["full_name"]
            node["full_name"] = found
        if node["party"] != party:
            self._logger.debug("%s %% %s" % (node["party"], party))
            node["party"] = party
        # self._logger.debug(node["party"])
        # self._logger.debug(node["constituency"])
        self._logger.debug("..................")
        self.db.save("%s_parse" % self.PREFIX, node)


def parse(**kwargs):
    ParseMps(**kwargs).run()