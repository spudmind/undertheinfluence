# -*- coding: utf-8 -*-
import logging
from utils import mongo
from utils import entity_resolver


class ParseLords():
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.resolver = entity_resolver.MasterEntitiesResolver()
        self.PREFIX = "lords"
        if kwargs["refreshdb"]:
            self.db.drop("%s_parse" % self.PREFIX)

    def run(self):
        _all_lords = self.db.fetch_all("%s_scrape" % self.PREFIX, paged=False)
        for doc in _all_lords:
            self._parse(doc)

    def _parse(self, node):
        found = self.resolver.find_lord(node["full_name"])
        party = self.resolver.find_party(node["party"])
        self._logger.debug("\n..................")
        self._logger.debug(found)
        if node["full_name"] != found:
            self._logger.debug("*** also known as: %s" % node["full_name"])
            node["also_known_as"] = found
        if node["party"] != party:
            node["party"] = party
        self._logger.debug(party)
        node["number_of_terms"] = len(node["terms"])
        self._logger.debug("..................")
        self.db.save("%s_parse" % self.PREFIX, node)


def parse(**kwargs):
    ParseLords(**kwargs).run()