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
                print "\n", entry["mp"]
                for category in entry["interests"]:
                    self._parse_category(category)

    def _parse_category(self, data):
        category_name = data["category_name"]
        if category_name == "Directorships":
            #self._display_record(data)
            #self._parse_list_record(data)
            pass
        elif category_name == "Remunerated directorships":
            #self._display_record(data)
            #self._parse_list_record(data)
            pass
        elif category_name == "Remunerated employment, office, profession etc":
            #self._display_record(data)
            #self._parse_list_record(data)
            pass
        elif category_name == "Remunerated employment, office, profession, etc_":
            #self._display_record(data)
            #self._parse_list_record(data)
            pass
        elif category_name == "Clients":
            #self._display_record(data)
            #self._parse_clients(data)
            pass
        elif category_name == "Land and Property":
            #self._display_record(data)
            #self._parse_land_ownership(data)
            pass
        elif category_name == "Shareholdings":
            #self._display_record(data)
            #self._parse_unstructured_record(data)
            pass
        elif category_name == "Registrable shareholdings":
            #self._display_record(data)
            #self._parse_unstructured_record(data)
            pass
        elif category_name == "Sponsorships":
            #self._display_record(data)
            #self._parse_sponsorships(data)
            pass
        elif category_name == "Sponsorship or financial or material support":
            #self._display_record(data)
            #self._parse_sponsorships(data)
            pass
        elif category_name == "Overseas visits":
            #self._display_record(data)
            #self._parse_structured_record(data)
            pass
        elif category_name == "Gifts, benefits and hospitality (UK)":
            #self._display_record(data)
            #self._parse_gifts(data)
            pass
        elif category_name == "Overseas benefits and gifts":  #done
            #self._display_record(data)
            #self._parse_gifts(data)
            pass
        elif category_name == "Miscellaneous":  #needs a special parser
            self._display_record(data)
            self._parse_miscellaneous_record(data)
            pass
        else:
            print "   *", category_name

    def _parse_list_record(self, data):
        company_name, renumeration = None, None
        for record in data["records"]:
            first = record[0].lower()
            if "(of " == first[:4] or "of " == first[:3]:
                if len(record) > 1:
                    first = record[1]
                continue
            else:
                company_details = self._get_entities(first)
                if company_details:
                    company_name = company_details[0]
                    payments = [self._find_money(item) for item in record]
                    dates = [self._find_dates(item) for item in record]
                    renumeration = zip(payments, dates)
                else:
                    print "########", record
            print " ---> donor:", company_name
            print " ---> renumeration:", renumeration
            print "-"

    def _parse_structured_record(self, data):
        for record in data["records"]:
            clean_parse = False
            company_name, amount, destination = None, None, None
            vist_dates, purpose, registered = None, None, None
            if len(record) == 7:
                company_name = self._find_company(record[0])
                if not company_name:
                    company_name = record[0].split(":")[1].strip()
                amount = self._find_money(record[2])
                destination = self._get_entities(record[3])
                vist_dates = record[4].split(":")[1].strip()
                purpose = record[5].split(":")[1].strip()
                registered = self._find_dates(record[6])
                clean_parse = True
            elif len(record) != 7:
                print "** != 7: ", len(record)
                for item in record:
                    if "Name of donor" in item:
                        company_name = self._find_company(record[0])
                        if not company_name:
                            company_name = record[0].split(":")[1].strip()
                    elif "Amount of donation" in item:
                        amount = self._find_money(item)
                    elif "Destination of visit" in item:
                        destination = self._get_entities(item)
                    elif "Date of visit" in item:
                        vist_dates = item.split(":")[1].strip()
                    elif "Purpose of visit" in item:
                        purpose = item.split(":")[1].strip()
                    elif "Registered" in item:
                        registered = self._find_dates(item)
            print " ---> donor:", company_name
            print " ---> dest/cost:", destination, amount
            print "-"

    def _parse_sponsorships(self, data):
        for record in data["records"]:
            clean_parse = False
            company_name, amount = None, None
            donor_status, registered = None, None
            if len(record) == 1:
                continue
            elif len(record) == 5:
                company_name = self._find_company(record[0])
                if not company_name and ":" in record[0]:
                    company_name = record[0].split(":")[1].strip()
                amount = self._find_money(record[2])
                donor_status = record[3].split(":")[1].strip()
                registered = self._find_dates(record[4])
                clean_parse = True
            else:
                for item in record:
                    if "Name of donor" in item:
                        company_name = self._find_company(record[0])
                        if not company_name and ":" in item:
                            company_name = item.split(":")[1].strip()
                    elif "Amount of donation" in item:
                        amount = self._find_money(item)
                    elif "Donor status" in item:
                        donor_status = item.split(":")[1].strip()
                    elif "Registered" in item:
                        registered = self._find_dates(item)
            print " ---> donor:", company_name
            print " ---> status/cost:", donor_status, amount
            print "-"

    def _parse_gifts(self, data):
        for record in data["records"]:
            clean_parse = False
            company_name, amount, nature = None, None, None
            donor_status, registered = None, None
            if len(record) == 1:
                continue
            elif len(record) == 7:
                company_name = self._find_company(record[0])
                if not company_name and ":" in record[0]:
                    company_name = record[0].split(":")[1].strip()
                amount = self._find_money(record[2])
                nature = record[2].split(":")[1].strip()
                receipt = self._find_dates(record[3])
                accepted = self._find_dates(record[4])
                if ":" in record[5]:
                    donor_status = record[5].split(":")[1].strip()
                registered = self._find_dates(record[6])
                clean_parse = True
            else:
                for item in record:
                    if "Name of donor" in item:
                        company_name = self._find_company(record[0])
                        if not company_name and ":" in item:
                            company_name = item.split(":")[1].strip()
                    elif "Amount of donation" in item:
                        amount = self._find_money(item)
                        nature = item.split(":")[1].strip()
                    elif "Date of receipt" in item:
                        receipt = self._find_dates(item)
                    elif "Date of acceptance" in item:
                        accepted = self._find_dates(item)
                    elif "Donor status" in item:
                        donor_status = item.split(":")[1].strip()
                    elif "Registered" in item:
                        registered = self._find_dates(item)
            print " ---> donor:", company_name
            print " ---> status/cost:", donor_status, amount
            print "-"

    def _parse_land_ownership(self, data):
        for record in data["records"]:
            for item in record:
                locations = self._get_entities(item)
                dates = self._find_dates(item)
                if locations:
                    print "---->", locations, dates

    def _parse_clients(self, data):
        for record in data["records"]:
            print len(record)
            if len(record) == 1:
                print "++++++>", record
                self._parse_unstructured_record(data)
            elif len(record) > 1:
                check = record[-2].lower()
                if "payment of" in check or "fees of" in check or "received" in check:
                    self._parse_list_record(data)
                else:
                    self._parse_unstructured_record(data)

    #might need more work
    def _parse_unstructured_record(self, data):
        for record in data["records"]:
            for item in record:
                if "(of " == item[:4].lower() or "of " == item[:3].lower():
                    continue
                else:
                    if ";" in item:
                        line_test = re.sub('\(.+?\)\s*', '', item)
                        if len(line_test.split(";")) == 2:
                            company_name = item.split(";")[0].strip().rstrip('.')
                            company_name = re.sub('\(.+?\)\s*', '', company_name)
                            dates = self._find_dates(item.split(";")[1])
                        else:
                            company_name = self._find_company(item)
                            dates = self._find_dates(item)
                    else:
                        company_name = self._find_company(item)
                        dates = self._find_dates(item)
                    if company_name:
                        print "---->", company_name, dates

    def _parse_miscellaneous_record(self, data):
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
        money = None
        money = re.findall(self.money_search, data)
        return money

    def _get_entities(self, data):
        return self.entity_extractor.get_entities(data)

    @staticmethod
    def _display_record(data):
        print "   *", data["category_name"]
        for record in data["records"]:
            for item in record:
                print "     ", item
            print "---"

