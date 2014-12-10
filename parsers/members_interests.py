# -*- coding: utf-8 -*-
import re
from data_interfaces import mongo


class MembersInterestsParser:
    def __init__(self, entity_extractor):
        self.entity_extractor = entity_extractor
        self.cache = mongo.MongoInterface()
        self.all_interests = list(self.cache.db.mps_interests.find())
        self.money_search = ur'([£$€])(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        self.date_search = ur'(\d{1,2}\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4})'

    def run(self):
        for documents in self.all_interests:
            print documents["file_name"]
            for entry in documents["contents"]:
                print "\n",entry["mp"]
                for category in entry["interests"]:
                    self._parse_category(category)

    def _parse_category(self, data):
        category_name = data["category_name"]
        if category_name == "Directorships":
            #self._parse_directorships(data)
            pass
        elif category_name == "Remunerated employment, office, profession etc":
            #self._parse_directorships(data)
            pass
        elif category_name == "Remunerated employment, office, profession, etc_":
            #self._parse_directorships(data)
            pass
        elif category_name == "Clients":
            #self._parse_records(data)
            pass
        elif category_name == "Overseas visits":
            #self._parse_structured_record(data)
            pass
        elif category_name == "Land and Property": #needs a special parser
            #self._parse_records(data)
            pass
        elif category_name == "Shareholdings":  #needs a special parser
            print "   *", category_name
            self._parse_unstructured_record(data)
            self._display_record(data)
        elif category_name == "Sponsorships":  #needs a special parser
            #self._parse_records(data)
            pass
        elif category_name == "Sponsorship or financial or material support":  #needs a special parser
            #self._parse_list_records(data)
            pass
        elif category_name == "Gifts, benefits and hospitality (UK)":  #needs a special parser
            #self._parse_records(data)
            pass
        elif category_name == "Registrable shareholdings":  #needs a special parser
            #self._parse_list_records(data)
            pass
        elif category_name == "Remunerated directorships":
            #self._parse_list_records(data)
            pass
        elif category_name == "Overseas benefits and gifts":  #See my entry in Category 2 + needs a special parser
            #self._parse_list_records(data)
            pass
        elif category_name == "Miscellaneous":  #needs a special parser
            #self._parse_records(data)
            pass
        else:
            print "   *", category_name

    def _parse_list_record(self, data):
        for record in data["records"]:
            company_details = self._get_entities(record[0])
            if company_details:
                company_name = company_details[0]
                payments = [self._find_money(item) for item in record]
                dates = [self._find_dates(item) for item in record]
                print "-->", company_name
                for item in record:
                    print "     ", item
                renumeration = zip(payments, dates)
                print renumeration
                print "---"
            else:
                print record

    def _parse_structured_record(self, data):
        for record in data["records"]:
            company_details = self._get_entities(record[0])
            if company_details:
                company_name = company_details[0]
                print "---->", company_name

    def _parse_unstructured_record(self, data):
        for record in data["records"]:
            for item in record:
                company_name = self._find_company(item)
                dates = self._find_dates(item)
                if company_name:
                    print "---->", company_name, dates

    def _find_company(self, data):
        name = None
        company_details = self._get_entities(data)
        if company_details:
            for guess in company_details:
                if len(guess) < 3:
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

    def _find_dates(self, data):
        dates = re.findall(self.date_search, data)
        if dates:
            return dates
        else:
            return None

    def _find_money(self, data):
        money = re.search(self.money_search, data)
        if money:
            amount = money.groups()[1:]
            return amount[0]
        else:
            return None

    def _get_entities(self, data):
        return self.entity_extractor.get_entities(data)

    @staticmethod
    def _display_record(data):
        for record in data["records"]:
            for item in record:
                print "     ", item
        print "---"

