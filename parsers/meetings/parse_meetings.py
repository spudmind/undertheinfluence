# -*- coding: utf-8 -*-
import logging
from utils import mongo
from utils import entity_resolver


class ParseMeetings():
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.resolver = entity_resolver.MasterEntitiesResolver()
        self.PREFIX = "meetings"
        if kwargs["refreshdb"]:
            self.db.drop("%s_parse" % self.PREFIX)

    def run(self):
        _all_meetings = self.db.fetch_all("%s_scrape" % self.PREFIX, paged=False)
        for doc in _all_meetings:
            print "---"
            print doc["title"]
            print doc["department"]
            print doc["organisation"]
            print doc["name"]


def parse(**kwargs):
    ParseMeetings(**kwargs).run()