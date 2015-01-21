from fuzzywuzzy import process
from utils import mongo
from utils import config
from utils import entity_extraction
import re


class MasterEntitiesResolver:
    def __init__(self, ):
        self.fuzzy_match = process
        self.cache = mongo.MongoInterface()
        self.entity_extractor = entity_extraction.NamedEntityExtractor()
        self.master_mps = self.cache.db.master_mps
        self.master_lords = self.cache.db.master_lords
        self.return_first_entity = True
        self.master_mps = list(self.cache.db.master_mps.find({"name": 1}))
        self.master_lords = list(self.cache.db.master_lords.find({"name": 1}))
        self.mapped_mps = config.mapped_mps
        self.mapped_companies = config.mapped_companies
        self.mapped_lords = config.mapped_lords
        self.company_entities = config.company_entities
        self.party_entities = config.party_entities
        self.mapped_parties = config.mapped_parties
        self.prefixes = config.prefixes

    def get_entities(self, search_string):
        entities = self.entity_extractor.get_entities(search_string)
        if self.return_first_entity:
            if entities and isinstance(entities, list):
                return entities[0]
        else:
            return entities

    def find_mp(self, search):
        name = search
        for incorrect, correct in self.mapped_mps:
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

    def find_lord(self, search):
        name = search
        for incorrect, correct in self.mapped_lords:
            if incorrect in search:
                name = correct
        if self.master_lords:
            cand = self.fuzzy_match.extractOne(name, self.master_lords)
            print name
            print cand
            if cand[1] > 80:
                name = cand[0]
        return name

    def find_party(self, search_string):
        name = None
        for entry in self.party_entities:
            if entry in search_string:
                name = entry
        for incorrect, correct in self.mapped_parties:
            if incorrect in search_string or incorrect == name:
                name = correct
        if not name:
            if self.party_entities:
                cand = self.fuzzy_match.extractOne(
                    name, self.party_entities
                )
                if cand[1] > 80:
                    name = cand[0]
        return name

    def find_donor(self, search_string, delimiter=";", fuzzy_delimit=True):
        name = None
        for entry in self.company_entities:
            if entry in search_string:
                name = entry
        if not name:
            if delimiter in search_string:
                if "accommodation" in search_string.lower():
                    name = self._parse_donor(search_string)
                else:
                    line_test = re.sub('\(.+?\)\s*', '', search_string)
                    if len(line_test.rstrip(delimiter).split(delimiter)) == 2:
                        demlimited = search_string.split(delimiter)[0]
                        company_name = demlimited.strip().rstrip('.')
                        new_search = demlimited.strip().rstrip('.') + "."
                        if fuzzy_delimit:
                            name = self._parse_donor(new_search)
                            if not name:
                                # TODO edit this to just remove (a) or (b)
                                name = re.sub('\(.+?\)\s*', '', company_name)
                        else:
                            name = company_name
        if not name:
            name = self._parse_donor(search_string)
        if name:
            for incorrect, correct in self.mapped_companies:
                if incorrect in name:
                    name = correct
        return name

    def _parse_donor(self, search):
        if self.return_first_entity:
            candidate = self.get_entities(search)
            if isinstance(candidate, list):
                return candidate[0]
            else:
                return candidate
        else:
            return self._get_best_entity(search)

    def _get_best_entity(self, search):
        name = None
        candidates = self.get_entities(search)
        if candidates:
            for guess in candidates:
                if len(guess) < 3:
                    print guess
                    print len(guess)
                    continue
                elif guess == "Sole":
                    continue
                elif "plc" or "ltd" or "limited" in guess.lower():
                    name = guess
                    break
                else:
                    name = guess
                    break
        return name