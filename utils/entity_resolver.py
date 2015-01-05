from fuzzywuzzy import process
from utils import mongo


class MasterEntitiesResolver:
    def __init__(self, ):
        self.fuzzy_match = process
        self.cache = mongo.MongoInterface()
        self.master_data = self.cache.db.master_mps
        self.master_mps = [
            x["name"] for x in list(self.master_data.find())
        ]
        self.known_incorrect = [
            (u"Ian Paisley Jnr", u"Ian Paisley"),
            (u"Nicholas Boles", u"Nick Boles"),
            (u"Nicholas Clegg", u"Nick Clegg"),
            (u"Vincent Cable", u"Vince Cable"),
            (u"Brian H Donohoe", u"Brian Donohoe"),
            (u"Susan Elan Jones", u"Susan Jones"),
            (u"Jeffrey M Donaldson", u"Jeffrey Donaldson"),
            (u"Edward Miliband", u"Ed Miliband"),
            (u"Edward Balls", u"Ed Balls"),
        ]
        self.prefixes = [
            "Sir "
        ]

    def find_mp(self, search):
        name = search
        for incorrect, correct in self.known_incorrect:
            if incorrect in search:
                name = correct
        for p in self.prefixes:
            if p in name:
                name = name.lstrip(p)
        if self.master_mps:
            cand = self.fuzzy_match.extractOne(name, self.master_mps)
            if cand[1] > 80:
                name = cand[0]
        return name
