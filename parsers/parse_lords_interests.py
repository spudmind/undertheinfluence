# -*- coding: utf-8 -*-
import re
import logging
from utils import mongo
from utils import entity_extraction
from utils import entity_resolver


class LordsInterestsParser:
    def __init__(self):
        self._logger = logging.getLogger('')

    def run(self):
        self.entity_extractor = entity_extraction.NamedEntityExtractor()
        self.entity_resolver = entity_resolver.MasterEntitiesResolver()
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.scraped_lords_interests
        self.all_interests = []
        self.money_search = ur'([£$€])(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        self.date_search = ur'(\d{1,2}\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4})'

        self.all_interests = list(self.cache_data.find())
        for documents in self.all_interests:
            file_name = documents["file_name"]
            for lord in documents["contents"]:
                resolved_name = self.entity_resolver.find_lord(lord["name"])
                self._logger.debug("\n%s" % resolved_name)
                categories = self._get_category_data(lord["interests"])
                lord_data = {
                    "lord": resolved_name,
                    "interests": categories,
                    "file_name": file_name
                }
                self.cache.db.parsed_lords_interests.save(lord_data)

    def _get_category_data(self, categories):
        categories_data = []
        for category in categories:
            cat_data = {
                "category_name": category["category_name"],
                "category_records": self._parse_category(category)
            }
            # self._logger.debug("\n%s\n" % cat_data)
            categories_data.append(cat_data)
        return categories_data

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
            return self._parse_clients(data)
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
            self._logger.debug("   * \s" % category_name)

    def _parse_list_record(self, data):
        company_name, remuneration = None, None
        records = []
        for record in data["records"]:
            company_name = self.entity_resolver.find_donor(record)
            if company_name:
                payment = self._find_money(record)
                date = self._find_dates(record)
                remuneration = zip([payment], [date])
            else:
                self._logger.debug("######## %s" % record)
            self._logger.debug(" ---> donor: %s" % company_name)
            self._logger.debug(" ---> remuneration: %s" % remuneration)
            # self._logger.debug(" ---> full record: %s" % record)
            self._logger.debug("-")
            entry = {
                "interest": company_name,
                "remuneration": self._cleanup_remuneration(remuneration),
                "raw_record": record
            }
            records.append(entry)
        return records

    def _parse_structured_record(self, data):
        records = []
        for item in data["records"]:
            clean_parse = False
            company_name, amount, destination = None, None, None
            visit_dates, purpose, registered = None, None, None
            if "Name of donor" in item:
                company_name = self.entity_resolver.find_donor(item)
                if not company_name:
                    company_name = self._split_if_colon(item)
            elif "Amount of donation" in item:
                amount = [y for x, y in self._find_money(item)]
            elif "Destination of visit" in item:
                destination = self.entity_resolver.get_entities(item)
            elif "Date of visit" in item:
                visit_dates = self._split_if_colon(item)
            elif "Purpose of visit" in item:
                purpose = self._split_if_colon(item)
            elif "Registered" in item:
                registered = self._find_dates(item)
            self._logger.debug(" ---> donor: %s" % company_name)
            self._logger.debug(" ---> dest/cost: %s %s" % (destination, amount))
            self._logger.debug("-")
            entry = {
                "interest": company_name,
                "remuneration": amount,
                "purpose": purpose,
                "vist_dates": visit_dates,
                "registered": registered,
                "raw_record": item
            }
            records.append(entry)
        return records

    def _parse_unstructured_record(self, data):
        records = []
        for item in data["records"]:
            company_name = None
            if "(of " == item[:4].lower() or "of " == item[:3].lower():
                continue
            else:
                company_name = self.entity_resolver.find_donor(item)
                dates = self._find_dates(item)
                if company_name:
                    self._logger.debug("----> %s %s" % (company_name, dates))
                entry = {
                    "interest": company_name,
                    "registered": dates,
                    "raw_record": item
                }
                records.append(entry)
        return records

    def _parse_sponsorships(self, data):
        return []

    def _parse_gifts(self, data):
        records = []
        for item in data["records"]:
            clean_parse = False
            company_name, amount, nature, accepted = None, None, None, None
            donor_status, registered, receipt = None, None, None
            if "Name of donor" in item:
                company_name = self.entity_resolver.find_donor(item)
                if not company_name and ":" in item:
                    company_name = self._split_if_colon(item)
            elif "Amount of donation" in item:
                amount = [y for x, y in self._find_money(item)]
                nature = self._split_if_colon(item)
            elif "Date of receipt" in item:
                receipt = self._find_dates(item)
            elif "Date of acceptance" in item:
                accepted = self._find_dates(item)
            elif "Donor status" in item:
                donor_status = self._split_if_colon(item)
            elif "Registered" in item:
                registered = self._find_dates(item)
            self._logger.debug(" ---> donor: %s" % company_name)
            self._logger.debug(" ---> status/cost: %s %s" % (donor_status, amount))
            self._logger.debug("-")
            entry = {
                "interest": company_name,
                "remuneration": amount,
                "nature": nature,
                "receipt": receipt,
                "accepted": accepted,
                "registered": registered,
                "raw_record": item
            }
            records.append(entry)
        return records

    def _parse_land_ownership(self, data):
        records = []
        for item in data["records"]:
            locations = self.entity_resolver.get_entities(item)
            dates = self._find_dates(item)
            if locations:
                self._logger.debug("----> %s %s" % (locations, dates))
            entry = {
                "interest": locations,
                "raw_record": item
            }
            records.append(entry)
        return records

    def _parse_clients(self, data):
        for record in data["records"]:
            # TODO: This can't be right?!
            self._parse_unstructured_record(data)
            break

    def _parse_miscellaneous_record(self, data):
        records = []
        for item in data["records"]:
            company_name = self.entity_resolver.find_donor(item)
            dates = self._find_dates(item)
            if company_name:
                self._logger.debug("----> %s %s" % (company_name, dates))
                entry = {
                    "interest": company_name,
                    "registered": dates,
                    "raw_record": item
                }
                records.append(entry)
        return records

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

    def _show_record(self, data):
        self._logger.debug("   * %s" % data["category_name"])
        for item in data["records"]:
            self._logger.debug("     %s" % item)
        self._logger.debug("---")

    def _cleanup_remuneration(self, entry):
        new_list = []
        if entry != [([], None)]:
            if len(entry[0]) > 0:
                # self._logger.debug("%s %s" % (entry[0][0][1], entry[1]))
                if entry[1] and len(entry[1]) > 1:
                    received = entry[1][0]
                    registered = entry[1][1]
                else:
                    received = "Unknown"
                    registered = "Unknown"
                new_entry = {
                    "amount": entry[0][0][1],
                    "received": received,
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

    def _print_out(self, key, value):
        self._logger.debug("  %-30s%-20s" % (key, value))
