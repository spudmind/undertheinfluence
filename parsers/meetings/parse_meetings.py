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
        titles = []
        for doc in _all_meetings:
            print "---"
            titles.append(doc["title"])
            for field in ["title", "department", "organisation", "name"]:
                if field in doc:
                    print "%s: " % field, doc[field]
            print doc["title"]
        print "\n\ntitle count:", set(titles)


def parse(**kwargs):
    ParseMeetings(**kwargs).run()