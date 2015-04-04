# -*- coding: utf-8 -*-
import logging
from utils import mongo
from utils import config
from utils import entity_resolver


class ParseMeetings():
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()
        self.resolver = entity_resolver.MasterEntitiesResolver()
        self.lords_titles = config.lords_titles
        self.secretarial_titles = ["secretaries", "secretary"]
        self.ministerial_titles = "ministerial"
        self.PREFIX = "meetings"
        if kwargs["refreshdb"]:
            self.db.drop("%s_parse" % self.PREFIX)

    def run(self):
        self._logger.debug("Parsing Ministerial Meetings")
        _all_meetings = self.db.fetch_all("%s_scrape" % self.PREFIX, paged=False)
        titles = []
        for doc in _all_meetings:
            titles.append(doc["title"])
            if any(title in doc["title"] for title in self.secretarial_titles):
                #self._parse_secretarial(doc)
                pass
            if "ministerial" in doc["title"].lower():
                self._parse_ministerial(doc)

        print "\n\ntitle count:", len(set(titles))

    def _parse_ministerial(self, meeting):
        orgs = []
        host = {}
        problems = [
            "London",
            "UK Anti",
            "doping",
            "Sochi",
            "Army",
            "British",
            "Home Enteraintment Gp",
            "Justice",
            "Co",
            "Organisation for Economic Co",  # oecd
            "AeroSpace",  # ADS
            "Rolls"
        ]
        if "organisation" in meeting:
            orgs = self._parse_organisation(meeting["organisation"].strip())
        for org in orgs:
            self._logger.debug("... %s" % org)
            date = None
            purpose = None
            if "name" in meeting:
                host = self._parse_host(meeting["name"].strip())
            if "date" in meeting and len(meeting["date"]) == 10 \
                    and "-" in meeting["date"]:
                date = meeting["date"]
            if "purpose" in meeting:
                purpose = meeting["purpose"]
            entry = {
                "title": meeting["title"],
                "department": meeting["department"],
                "host_name": host["name"],
                "host_position": host["position"],
                "organisation": org,
                "date": date,
                "source": meeting["source"],
                "purpose": purpose,
                "published_at": meeting["published_at"],
                "meeting_type": "Ministerial Meetings",
            }
            for problem in problems:
                if problem == org:
                    print "\n\n", meeting, "\n\n"
            self.db.save("%s_parse" % self.PREFIX, entry)

    def _parse_secretarial(self, meeting):
        if "name" in meeting:
            print meeting["name"]
            print self._resolve_name(meeting["name"])
            print "---\n"

    def _parse_organisation(self, org_string):
        separators = ["/", ",", ";", "\n", "-"]
        organisations = []
        if any(sep in org_string for sep in separators):
            for sep in separators:
                if sep in org_string:
                    orgs = org_string.split(sep)
                    if len(orgs) == 2 and sep == ",":
                        organisations.append(org_string)
                    else:
                        for org in orgs:
                            if len(org.strip()) > 1:
                                name = self._resolve_influencer(org.strip())
                                organisations.append(name)
                    break
        else:
            name = self._resolve_influencer(org_string.strip())
            organisations.append(name)
        return organisations

    def _parse_host(self, name_string):
        positions = ["minister", "secretary"]
        name, position = self._synatic_parse(name_string)
        if not name:
            name, position = self._entity_parse(name_string)
        # if still name not found see if it's just the position
        if not name:
            if any(pos in name_string.lower() for pos in positions):
                position = name_string
        return {"name": name, "position": position}

    def _synatic_parse(self, name_string):
        name_string = u"{}".format(name_string)
        rear, front = {}, {}
        name, position = None, None
        separators = [" - ", u" \x96 ", ";", ","]
        # try finding the name using the string syntax
        if any(sep in name_string for sep in separators):
            for sep in separators:
                if sep in name_string:
                    sent = name_string.split(sep)
                    # check end of string
                    name = self._resolve_politician(sent[-1].strip())
                    rear = {"name": name, "sep": sep}
                    if name:
                        break
                    if not name:
                        # check beginning of string
                        name = self._resolve_politician(sent[0].strip())
                        front = {"name": name, "sep": sep}
                        if name:
                            break
            # if name found try get the position
            if name:
                if rear["name"]:
                    sent = name_string.split(rear["sep"])
                    position = rear["sep"].join(sent[:-1]).strip()
                elif front["name"]:
                    sent = name_string.split(front["sep"])
                    position = front["sep"].join(sent[1:]).strip()
        return name, position

    def _entity_parse(self, name_string):
        position = None
        name = self._resolve_politician(name_string)
        if name:
            name_split = name.split(" ")
            position = name_string.split(name_split[0])[0]
        return name, position

    def _resolve_influencer(self, candidate):
        if "mp" in candidate.lower():
            name = self._resolve_politician(candidate)
        else:
            name = self.resolver.find_influencer(candidate)
        return candidate if name is None else name

    def _resolve_politician(self, candidate):
        if any(title in candidate for title in self.lords_titles):
            name = self.resolver.find_lord(candidate)
        else:
            name = self.resolver.find_mp(candidate)
        return name

    def _resolve_name(self, candidate):
        name = self.resolver.get_entities(candidate)
        return candidate if name is None else name


def parse(**kwargs):
    ParseMeetings(**kwargs).run()