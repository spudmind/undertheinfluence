import re
import logging
from fuzzywuzzy import process as fuzzy_match
from utils import mongo
from utils import config
from utils import entity_extraction


class MasterEntitiesResolver:
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.cache = mongo.MongoInterface()
        self.entity_extractor = entity_extraction.NamedEntityExtractor()
        self.return_first_entity = True
        self.master_mps = [
            x["name"] for x in list(self.cache.db.master_mps.find())
        ]
        self.master_lords = [
            x["name"] for x in list(self.cache.db.master_lords.find())
        ]
        self.mapped_mps = config.mapped_mps
        self.mapped_donors = config.mapped_donors
        self.mapped_lords = config.mapped_lords
        self.donor_entities = config.donor_entities
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
        found = False
        for p in self.prefixes:
            if p in search:
                search = search.lstrip(p)
        if self.master_mps != []:
            guess, accuracy = fuzzy_match.extractOne(search, self.master_mps)
            if accuracy > 80:
                found = True
                search = guess
        for incorrect, correct in self.mapped_mps:
            if incorrect in search:
                found = True
                search = correct
        return search if found else None

    def find_lord(self, search):
        found = False
        if self.master_lords != []:
            guess, accuracy = fuzzy_match.extractOne(search, self.master_lords)
            if accuracy > 80:
                found = True
                search = guess
        for incorrect, correct in self.mapped_lords:
            if incorrect in search:
                found = True
                search = correct
        return search if found else None

    def find_party(self, search):
        name = None
        for entry in self.party_entities:
            if entry in search:
                name = entry
        for incorrect, correct in self.mapped_parties:
            if incorrect in search or incorrect == name:
                name = correct
        if not name:
            cand = fuzzy_match.extractOne(search, self.party_entities)
            if cand[1] > 80:
                name = cand[0]
        return name

    def find_donor(self, search_string, delimiter=";", fuzzy_delimit=True):
        name = None
        for entry in self.donor_entities:
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
            for incorrect, correct in self.mapped_donors:
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
                    self._logger.debug(guess)
                    self._logger.debug(len(guess))
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
