# -*- coding: utf-8 -*-
import logging
from utils import mongo
from utils import entity_resolver


class MPsParser():
    def __init__(self):
        self._logger = logging.getLogger('spud')

    def run(self):
        self.db = mongo.MongoInterface()
        self.resolver = entity_resolver.MasterEntitiesResolver()

        #self._all_mps = list(self._cache_data.find())
        _all_mps = self.db.fetch_all('scraped_mp_info', paged=False)
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
        self.db.save('parsed_mp_info', node)
        # self._logger.debug(node["twfy_id"])
