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
        self.known_incorrect_mps = [
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
        self.known_missing_companies = [
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
            u"Transworld Publishers",
            u"Developing Markets Associates Ltd",
            u"Democracy Forum Ltd",
            u"Ambriel Consulting"
        ]
        self.known_political_parties = [
            u"Labour Party",
            u"Alliance Party of Northern Ireland"
            u"Alliance Party",
            u"Democratic Unionist Party",
            u"DUP",
            u"Sinn Fein",
            u"Conservative Party",
            u"Liberal Democrat Party",
            u"Liberal Democrats",
            u"Plaid Cymru",
            u"Independent",
            u"Social Democratic and Labour Party",
            u"Scottish National Party",
            u"Green Party",
            u"Speaker",
            u"UK Independence Party",
            u"UKIP",
            u"Co-operative Party",
            u"We Demand A Referendum Now",
            u"BNP",
            u"British National Party",
            u"NO2EU",
            u"English Democrats"
        ]
        self.known_incorrect_parties = [
            (u"DUP", u"Democratic Unionist Party"),
            (u"UKIP", u"UK Independence Party"),
            (u"Alliance Party", u"Alliance Party of Northern Ireland"),
            (u"Liberal Democrats", u"Liberal Democrat Party"),
            (u"BNP", u"British National Party")
        ]
        self.prefixes = [
            u"Sir ",
            u"Mr ",
            u"Ms "
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
        for incorrect, correct in self.known_incorrect_mps:
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

    def find_party(self, search_string):
        name = None
        for entry in self.known_political_parties:
            if entry in search_string:
                name = entry
        for incorrect, correct in self.known_incorrect_parties:
            if incorrect in search_string or incorrect == name:
                name = correct
        if not name:
            if self.known_political_parties:
                cand = self.fuzzy_match.extractOne(
                    name, self.known_political_parties
                )
                if cand[1] > 80:
                    name = cand[0]
        return name

    def find_donor(self, search_string, delimiter=";", fuzzy_delimit=True):
        name = None
        for entry in self.known_missing_companies:
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
            for incorrect, correct in self.known_incorrect_mps:
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