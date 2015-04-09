
import re
import logging
from fuzzywuzzy import process as fuzzy_match
from utils import mongo
from utils import config
from utils import entity_extraction


class MasterEntitiesResolver:
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self._db = mongo.MongoInterface()
        self._entity_extractor = entity_extraction.NamedEntityExtractor()
        self._master_mps = [
            x["name"] for x in self._db.fetch_all('master_mps', paged=False)
        ]
        self._master_lords = [
            x["name"] for x in self._db.fetch_all('master_lords', paged=False)
        ]
        self._master_positions = [
            x["position"] for x in self._db.fetch_all('master_positions', paged=False)
        ]
        self._mapped_positions = config.mapped_positions
        self._position_entities = config.position_entities
        self._mapped_mps = config.mapped_mps
        self._mapped_influencers = config.mapped_influencers
        self._mapped_lords = config.mapped_lords
        self._influencer_entities = config.influencer_entities
        self._party_entities = config.party_entities
        self._mapped_parties = config.mapped_parties
        self._mapped_lobbyists = config.mapped_lobbyists
        self._prefixes = config.prefixes
        self._sufixes = config.sufixes

    def get_entities(self, search_string, return_first_entity=True):
        found = None
        search_string = self._strip_prefix_sufix(search_string)
        entities = self._entity_extractor.get_entities(search_string)
        if return_first_entity:
            if len(entities) > 1:
                for entity in entities:
                    found = self._find_mapped_entity(entity)
                    if found:
                        break
                return found if found else entities[0]
            else:
                found = self._find_mapped_entity(search_string)
                return found if found else None
        else:
            return entities

    def find_mp(self, search):
        found = False
        search = self._strip_prefix_sufix(search)
        if isinstance(self._master_mps, list):
            guess, accuracy = fuzzy_match.extractOne(search, self._master_mps)
            if accuracy > 80:
                found = True
                search = guess
        for incorrect, correct in self._mapped_mps:
            if incorrect in search or incorrect == search:
                found = True
                search = correct
        return search if found else None

    def find_lord(self, search):
        found = False
        if isinstance(self._master_lords, list):
            guess, accuracy = fuzzy_match.extractOne(search, self._master_lords)
            if accuracy > 80:
                found = True
                search = guess
        for incorrect, correct in self._mapped_lords:
            if incorrect in search:
                found = True
                search = correct
        return search if found else None

    def find_position(self, search):
        name = None
        for entry in self._position_entities:
            if entry in search:
                name = entry
        if not name:
            if isinstance(self._master_lords, list):
                guess, accuracy = fuzzy_match.extractOne(search, self._master_positions)
                if accuracy > 80:
                    name = guess
        for incorrect, correct in self._mapped_positions:
            if incorrect in search:
                name = correct
        return name

    def find_party(self, search):
        name = None
        for entry in self._party_entities:
            if entry in search:
                name = entry
        if not name:
            cand = fuzzy_match.extractOne(search, self._party_entities)
            if cand[1] > 80:
                name = cand[0]
        for incorrect, correct in self._mapped_parties:
            if incorrect in search or incorrect == name:
                name = correct
        return name

    def find_influencer(self, search_string, delimiter=";", fuzzy_delimit=True):
        name = None
        for entry in self._influencer_entities:
            if entry in search_string:
                name = entry
        if not name:
            # TODO take this out / move to the members register
            if delimiter in search_string:
                if "accommodation" in search_string.lower():
                    name = self._parse_influencer(search_string)
                else:
                    line_test = re.sub('\(.+?\)\s*', '', search_string)
                    if len(line_test.rstrip(delimiter).split(delimiter)) == 2:
                        demlimited = search_string.split(delimiter)[0]
                        company_name = demlimited.strip().rstrip('.')
                        new_search = demlimited.strip().rstrip('.') + "."
                        if fuzzy_delimit:
                            name = self._parse_influencer(new_search)
                            if not name:
                                # TODO edit this to just remove (a) or (b)
                                name = re.sub('\(.+?\)\s*', '', company_name)
                        else:
                            name = company_name
        if not name:
            name = self._parse_influencer(search_string)
        if name:
            for incorrect, correct in self._mapped_influencers:
                if incorrect in name:
                    name = correct
        return name

    def _parse_influencer(self, search, return_first_entity=True):
        if return_first_entity:
            return self.get_entities(search)
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

    def map_lobby_agency(self, name):
        for incorrect, correct in self._mapped_lobbyists:
            if incorrect in name or incorrect == name:
                return correct
        return name

    def _find_mapped_entity(self, search_string):
        found = False
        mapped_entities = [self._mapped_mps, self._mapped_influencers, self._mapped_lords]
        for mapped in mapped_entities:
            for incorrect, correct in mapped:
                if incorrect in search_string or incorrect == search_string:
                    found = correct
                    break
        return found

    def _strip_prefix_sufix(self, text):
        for p in self._prefixes:
            if p in text.strip():
                text = text.strip().lstrip(p)
        for s in self._sufixes:
            if s in text.strip():
                text = text.strip().rstrip(s)
        return text