# -*- coding: utf-8 -*-
import re

from utils import mongo


class MembersInterestsParser:
    def __init__(self, entity_extractor):
        self.entity_extractor = entity_extractor
        self.cache = mongo.MongoInterface()
        self.all_interests = list(self.cache.db.scraped_mps_interests.find())
        self.money_search = ur'([£$€])(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        self.date_search = ur'(\d{1,2}\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4})'
        self.known_missing = [
            u"Mirror Group Newspapers",
            u"YouGov plc",
            u"Albion Community Power PLC"
        ]

    def run(self):
        for documents in self.all_interests:
            file_name = documents["file_name"]
            contents = []
            for entry in documents["contents"]:
                print "\n", entry["mp"]
                categories = []
                for category in entry["interests"]:
                    cat_data = {
                        "category_name": category["category_name"],
                        "category_records": self._parse_category(category)
                    }
                    #print "\n", cat_data, "\n"
                    categories.append(cat_data)
                mp_data = {
                    "mp": entry["mp"],
                    "categories": categories
                }
                contents.append(mp_data)
            data = {
                "file_name": file_name,
                "contents": contents
            }
            self.cache.db.parsed_mps_interests.save(data)

    def _parse_category(self, data):
        category_name = data["category_name"]
        if category_name == "Directorships":  # done
            self._show_record(data)
            return self._parse_list_record(data)
        elif category_name == "Remunerated directorships":  # done
            self._show_record(data)
            return self._parse_list_record(data)
            #pass
        elif category_name == "Remunerated employment, office, profession etc":  # done
            self._show_record(data)
            return self._parse_list_record(data)
            #pass
        elif category_name == "Remunerated employment, office, profession, etc_":  # done
            self._show_record(data)
            return self._parse_list_record(data)
            #pass
        elif category_name == "Clients":
            self._show_record(data)
            self._parse_clients(data)
            #pass
        elif category_name == "Land and Property":
            self._show_record(data)
            return self._parse_land_ownership(data)
            #pass
        elif category_name == "Shareholdings":
            self._show_record(data)
            return self._parse_unstructured_record(data)
            #pass
        elif category_name == "Registrable shareholdings":
            self._show_record(data)
            return self._parse_unstructured_record(data)
            #pass
        elif category_name == "Sponsorships":
            self._show_record(data)
            return self._parse_sponsorships(data)
            #pass
        elif category_name == "Sponsorship or financial or material support":
            self._show_record(data)
            return self._parse_sponsorships(data)
            #pass
        elif category_name == "Overseas visits":
            self._show_record(data)
            return self._parse_structured_record(data)
            #pass
        elif category_name == "Gifts, benefits and hospitality (UK)":
            self._show_record(data)
            return self._parse_gifts(data)
            #pass
        elif category_name == "Overseas benefits and gifts":
            self._show_record(data)
            return self._parse_gifts(data)
            #pass
        elif category_name == "Miscellaneous":
            self._show_record(data)
            return self._parse_miscellaneous_record(data)
            #pass
        else:
            print "   *", category_name

    def _parse_list_record(self, data):
        company_name, renumeration = None, None
        records = []
        for record in data["records"]:
            full_record = u"\n".join([item for item in record])
            if len(record) > 0:
                first = record[0]
                if "(of " == first[:4].lower() or "of " == first[:3].lower() or \
                        "  of " == first[:5].lower():
                    if len(record) > 1:
                        first = record[1]
                        print "yeahhhhh?"
                company_name = self._find_company(first)
                if company_name:
                    payments = [self._find_money(item) for item in record]
                    dates = [self._find_dates(item) for item in record]
                    renumeration = zip(payments, dates)
                else:
                    print "########", record
                print " ---> donor:", company_name
                print " ---> renumeration:", renumeration
                #print " ---> full record:", full_record
                print "-"
                entry = {
                    "interest": company_name,
                    "renumeration": self._cleanup_remuneration(renumeration),
                    "raw_record": full_record
                }
                records.append(entry)
        return records

    def _parse_structured_record(self, data):
        records = []
        for record in data["records"]:
            full_record = u"\n".join([item for item in record])
            clean_parse = False
            company_name, amount, destination = None, None, None
            visit_dates, purpose, registered = None, None, None
            if len(record) == 7:
                company_name = self._find_company(record[0])
                if not company_name:
                    company_name = self._split_if_colon(record[0])
                amount = [y for x, y in self._find_money(record[2])]
                destination = self._get_entities(record[3])
                visit_dates = self._split_if_colon(record[4])
                purpose = self._split_if_colon(record[5])
                registered = self._find_dates(record[6])
                clean_parse = True
            elif len(record) != 7:
                for item in record:
                    if "Name of donor" in item:
                        company_name = self._find_company(record[0])
                        if not company_name:
                            company_name = self._split_if_colon(record[0])
                    elif "Amount of donation" in item:
                        amount = self._find_money(item)
                    elif "Destination of visit" in item:
                        destination = self._get_entities(item)
                    elif "Date of visit" in item:
                        visit_dates = self._split_if_colon(item)
                    elif "Purpose of visit" in item:
                        purpose = self._split_if_colon(item)
                    elif "Registered" in item:
                        registered = self._find_dates(item)
            print " ---> donor:", company_name
            print " ---> dest/cost:", destination, amount
            print "-"
            entry = {
                "interest": company_name,
                "renumeration": amount,
                "purpose": purpose,
                "vist_dates": visit_dates,
                "registered": registered,
                "raw_record": full_record
            }
            records.append(entry)
        return records

    def _parse_unstructured_record(self, data):
        records = []
        for record in data["records"]:
            for item in record:
                company_name = None
                if "(of " == item[:4].lower() or "of " == item[:3].lower():
                    continue
                else:
                    company_name = self._find_company(item)
                    dates = self._find_dates(item)
                    if company_name:
                        print "---->", company_name, dates
                    entry = {
                        "interest": company_name,
                        "registered": dates,
                        "raw_record": item
                    }
                    records.append(entry)
        return records

    def _parse_sponsorships(self, data):
        records = []
        for record in data["records"]:
            full_record = u"\n".join([item for item in record])
            clean_parse = False
            company_name, amount = None, None
            donor_status, registered = None, None
            if len(record) == 1:
                continue
            elif len(record) == 5:
                company_name = self._find_company(record[0])
                if not company_name and ":" in record[0]:
                    company_name = self._split_if_colon(record[0])
                amount = [y for x, y in self._find_money(record[2])]
                donor_status = self._split_if_colon(record[3])
                registered = self._find_dates(record[4])
                clean_parse = True
            else:
                for item in record:
                    if "Name of donor" in item:
                        company_name = self._find_company(record[0])
                        if not company_name and ":" in item:
                            company_name = self._split_if_colon(item)
                    elif "Amount of donation" in item:
                        amount = self._find_money(item)
                    elif "Donor status" in item:
                        donor_status = self._split_if_colon(item)
                    elif "Registered" in item:
                        registered = self._find_dates(item)
            print " ---> donor:", company_name
            print " ---> status/cost:", donor_status, amount
            print "-"
            entry = {
                "interest": company_name,
                "renumeration": amount,
                "donor_status": donor_status,
                "registered": registered,
                "raw_record": full_record
            }
            records.append(entry)
        return records

    def _parse_gifts(self, data):
        records = []
        for record in data["records"]:
            clean_parse = False
            company_name, amount, nature, accepted = None, None, None, None
            donor_status, registered, receipt = None, None, None
            full_record = u"\n".join([item for item in record])
            if len(record) == 7:
                company_name = self._find_company(record[0])
                amount = self._find_money(record[2])
                nature = self._split_if_colon(record[2])
                receipt = self._find_dates(record[3])
                accepted = self._find_dates(record[4])
                donor_status = self._split_if_colon(record[5])
                registered = self._find_dates(record[6])
                clean_parse = True
            else:
                for item in record:
                    if "Name of donor" in item:
                        company_name = self._find_company(record[0])
                        if not company_name and ":" in item:
                            company_name = self._split_if_colon(item)
                    elif "Amount of donation" in item:
                        amount = self._find_money(item)
                        nature = self._split_if_colon(item)
                    elif "Date of receipt" in item:
                        receipt = self._find_dates(item)
                    elif "Date of acceptance" in item:
                        accepted = self._find_dates(item)
                    elif "Donor status" in item:
                        donor_status = self._split_if_colon(item)
                    elif "Registered" in item:
                        registered = self._find_dates(item)
            print " ---> donor:", company_name
            print " ---> status/cost:", donor_status, amount
            print "-"
            entry = {
                "interest": company_name,
                "renumeration": amount,
                "nature": nature,
                "receipt": receipt,
                "accepted": accepted,
                "registered": registered,
                "raw_record": full_record
            }
            records.append(entry)
        return records

    def _parse_land_ownership(self, data):
        records = []
        for record in data["records"]:
            full_record = u"\n".join([item for item in record])
            for item in record:
                locations = self._get_entities(item)
                dates = self._find_dates(item)
                if locations:
                    print "---->", locations, dates
                entry = {
                    "interest": locations,
                    "raw_record": full_record
                }
                records.append(entry)
        return records

    def _parse_clients(self, data):
        for record in data["records"]:
            if len(record) == 1:
                self._parse_unstructured_record(data)
            elif len(record) > 1:
                check = record[-2].lower()
                if "payment of" in check or "fees of" in check or "received" in check:
                    return self._parse_list_record(data)
                else:
                    return self._parse_unstructured_record(data)
            break

    def _parse_miscellaneous_record(self, data):
        records = []
        for record in data["records"]:
            for item in record:
                company_name = self._find_company(item)
                dates = self._find_dates(item)
                if company_name:
                    print "---->", company_name, dates
                    entry = {
                        "interest": company_name,
                        "registered": dates,
                        "raw_record": item
                    }
                    records.append(entry)
        return records

    def _find_company(self, data):
        name = None
        for entry in self.known_missing:
            if entry in data:
                name = entry
        if not name:
            if ";" in data:
                line_test = re.sub('\(.+?\)\s*', '', data)
                if len(line_test.rstrip(';').split(";")) == 2:
                    company_name = data.split(";")[0].strip().rstrip('.')
                    # TODO edit this to just remove (a) or (b)
                    name = re.sub('\(.+?\)\s*', '', company_name)
            else:
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
    def _show_record(data):
        print "   *", data["category_name"]
        for record in data["records"]:
            for item in record:
                print "     ", item
            print "---"

    @staticmethod
    def _cleanup_remuneration(data):
        new_list = []
        if data:
            for entry in data:
                if len(entry[0]) > 0:
                    #print entry[0][0][1], entry[1]
                    if entry[1] and len(entry[1]) > 1:
                        received = entry[1][0]
                        registered = entry[1][1]
                    else:
                        received = "Unknown"
                        registered = "Unknown"
                    new_entry = {
                        "amount": entry[0][0][1],
                        "recieved": received,
                        "registered": registered,
                    }
                    new_list.append(new_entry)
        else:
            new_list.append("No data")
        return new_list

    @staticmethod
    def _split_if_colon(text):
        result = text.strip()
        if len(text.split(":")) > 1:
            result = text.split(":")[1].strip()
        return result