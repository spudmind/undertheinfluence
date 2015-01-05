from fuzzywuzzy import process
from utils import mongo
from utils import entity_extraction
import re


class MasterEntitiesResolver:
    def __init__(self, ):
        self.fuzzy_match = process
        self.cache = mongo.MongoInterface()
        self.entity_extractor = entity_extraction.NamedEntityExtractor()
        self.master_data = self.cache.db.master_mps
        self.return_first_entity = True
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
            (u"Guardian News", u"Guardian News and Media Ltd"),
            (u"Guardian", u"Guardian News and Media Ltd"),
            (u"YouGov", u"YouGov PLC")
        ]
        self.known_missing = [
            u"IPSOS Mori",
            u"Ipsos MORI",
            u"Ipsos Mori",
            u"YouGov",
            u"ComRes",
            u"Social Investment Business Group",
            u"Mansfeider Kupfer Und Messing GMBH",
            u"Pembroke VCT plc",
            u"Woodlands Schools Ltd",
            u"Making It (UK) Ltd",
            u"Phoenix Life Assurance Ltd",
            u"Office of Gordon and Sarah Brown",
            u"The Independent",
            u"Transworld Publishers"
        ]
        self.prefixes = [
            "Sir "
        ]

    def get_entities(self, search_string):
        entities = self.entity_extractor.get_entities(search_string)
        if entities and len(entities) > 1:
            if self.return_first_entity:
                return entities[0]
        else:
            return entities

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

    def find_donor(self, search_string):
        name = None
        for entry in self.known_missing:
            if entry in search_string:
                name = entry
        if not name:
            if ";" in search_string:
                if "accommodation" in search_string.lower():
                    name = self._parse_donor(search_string)
                else:
                    line_test = re.sub('\(.+?\)\s*', '', search_string)
                    if len(line_test.rstrip(';').split(";")) == 2:
                        company_name = search_string.split(";")[0].strip().rstrip('.')
                        new_search = search_string.split(";")[0].strip().rstrip('.') + "."
                        name = self._parse_donor(new_search)
                        if not name:
                            # TODO edit this to just remove (a) or (b)
                            name = re.sub('\(.+?\)\s*', '', company_name)
        if not name:
            name = self._parse_donor(search_string)
        if name:
            for incorrect, correct in self.known_incorrect:
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