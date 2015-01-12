from utils import mongo
from utils import entity_resolver


class PartyFundingParser():
    def __init__(self):
        self._cache = mongo.MongoInterface()
        self._cache_data = self._cache.db.scraped_party_funding
        self._parsed_data = self._cache.db.parsed_party_funding
        self.resolver = entity_resolver.MasterEntitiesResolver()
        self._all_entries = []

    def run(self):
        self._all_entries = list(self._cache_data.find())
        for doc in self._all_entries:
            parsed = {}
            parsed["recipient"] = self._parse_recipient(
                doc["recipient"], doc["donee_type"], doc["recipient_type"]
            )
            parsed["donor_name"] = self.resolver.find_donor(
                doc["donor_name"], delimiter=",", fuzzy_delimit=False
            )
            parsed["donor_type"] = doc["donor_type"]
            parsed["donee_type"] = doc["donee_type"]
            parsed["recipient_type"] = doc["recipient_type"]
            parsed["donation_type"] = doc["donation_type"]
            parsed["value"] = doc["value"]
            parsed["purpose"] = doc["purpose"]
            parsed["nature_provision"] = doc["nature_provision"]
            parsed["ec_reference"] = doc["ec_reference"]
            parsed["company_reg"] = doc["company_reg"]
            parsed["is_sponsorship"] = doc["is_sponsorship"]
            parsed["6212"] = doc["6212"]
            parsed["recd_by"] = doc["recd_by"]
            parsed["received_date"] = doc["received_date"]
            parsed["reported_date"] = doc["reported_date"]
            parsed["accepted_date"] = doc["accepted_date"]
            #self._print_out("recipient", parsed["recipient"])
            #self._print_out("donee_type", parsed["donee_type"])
            #self._print_out("donor_name", parsed["donor_name"])
            #self._print_out("donor_type", parsed["donor_type"])
            #self._print_out("value", parsed["value"])
            if not parsed["recipient"]:
                self._print_dic(parsed)
                print "---\n"
            else:
                self._parsed_data.save(parsed)

    def _parse_recipient(self, entry, entry_type, recipient_type):
        if entry_type == "MP - Member of Parliament":
            result = self.resolver.find_mp(entry)
        elif entry_type == "Political Party" or \
                recipient_type == "Political Party":
            result = self.resolver.find_party(entry)
        else:
            result = self.resolver.get_entities(entry)
            if result and isinstance(result, list):
                result = result[0]
            else:
                result = entry
        return result

    @staticmethod
    def _print_out(key, value):
        print "  %-30s%-20s" % (key, value)

    @staticmethod
    def _print_dic(dictionary):
        for keys, values in dictionary.items():
            print " %-20s:%-25s" % (keys, values)