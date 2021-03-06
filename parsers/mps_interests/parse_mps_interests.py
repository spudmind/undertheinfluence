# -*- coding: utf-8 -*-
import re
import logging
from utils import mongo
from utils import entity_extraction
from utils import entity_resolver


money_search = ur'([£$€])(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
date_search = ur'(\d{1,2}\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4})'


class ParseMPsInterests:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        self.resolver = entity_resolver.MasterEntitiesResolver()
        self.db = mongo.MongoInterface()
        self.PREFIX = "mps_interests"
        if kwargs["refreshdb"]:
            self.db.drop("%s_parse" % self.PREFIX)

    def run(self):
        all_interests = self.db.fetch_all("%s_scrape" % self.PREFIX, paged=False)
        for doc in all_interests:
            # we currently ignore documents before this date,
            # because they're harder to parse
            if doc["date"] < "2010-09-06":
                continue

            # each document contains a day's recorded interests for an MP
            # document structure is:
            #   contents > interests / categories > interest
            # parsed output is a document per mp structured:
            #   mp > interests / categories > interest


            resolved_name = self._get_mp(doc["mp"])
            self._logger.debug("\n%s" % resolved_name)
            categories = self._get_category_data(doc["interests"])

            mp_data = {
                "mp": resolved_name,
                "interests": categories,
                "date": doc["date"],
                "source": doc["source"]
            }

            self.db.save("%s_parse" % self.PREFIX, mp_data)

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

    def _parse_category(self, record):

        # members interests are not structured at source &
        # each entry captured in free text
        # the record is a python list, with each line from the free text
        # stored as a list item

        # individual categories to conform to specific conventions
        # this function picks the appropriate parser for each convention

        #self._show_record(record)

        category_name = self._fix_categories(record["category_name"])

        self._logger.debug("* %s" % category_name)

        if category_name.lower() == "directorships":
            return self._parse_list_record(record)
        elif category_name.lower() == "remunerated directorships":
            return self._parse_list_record(record)
            #pass
        elif category_name.lower() == "remunerated employment, office, profession etc":
            return self._parse_list_record(record)
            #pass
        elif category_name.lower() == "remunerated employment, office, profession, etc_":
            return self._parse_list_record(record)
            #pass
        elif category_name.lower() == "clients":
            return self._parse_clients(record)
            #pass
        elif category_name.lower() == "land and property":
            pass
            #return self._parse_land_ownership(record)
            #pass
        elif category_name.lower() == "shareholdings":
            return self._parse_unstructured_record(record)
            #pass
        elif category_name.lower() == "registrable shareholdings":
            return self._parse_unstructured_record(record)
            #pass
        elif category_name.lower() == "sponsorships":
            return self._parse_sponsorships(record)
            #pass
        elif category_name.lower() == "sponsorship or financial or material support":
            return self._parse_sponsorships(record)
            #pass
        elif category_name.lower() == "overseas visits":
            return self._parse_travel_record(record)
            #pass
        elif category_name.lower() == "gifts, benefits and hospitality (UK)":
            return self._parse_gifts(record)
            #pass
        elif category_name.lower() == "overseas benefits and gifts":
            return self._parse_gifts(record)
            #pass
        elif category_name.lower() == "miscellaneous":
            return self._parse_unstructured_record(record)
            #pass
        elif category_name.lower() == "miscellaneous and unremunerated interests":
            return self._parse_unstructured_record(record)
            #pass
        elif category_name.lower() == "loans and other controlled transactions":
            # TODO write a parser for this
            pass
        else:
            self._logger.debug("   * %s" % category_name)

    def _parse_list_record(self, data):

        # this interest record follows the following format:
        # record[0] = interest name, with one exception
        # record[1:] remuneration & date details related to that interest

        interest_name, remuneration = None, None
        records = []
        for record in data["records"]:
            full_record = u"\n".join([item for item in record])
            if len(record) > 0:
                first = record[0]
                test = record[0].lower()

                # record[0] may not contain the interest name
                # e.g. in the Clients category members with multiple
                # directorships will entry which company the interests
                # are clients of.

                if "(of " == test[:4] or "of " == test[:3] or "  of " == test[:5]:
                    if len(record) > 1:
                        # if record[0] use next line as first record
                        first = record[1]
                interest_name = self.resolver.find_influencer(first)
                if interest_name:
                    # if no interest is found, skip record
                    payments = [self._find_money(item) for item in record]
                    dates = [self._find_dates(item) for item in record]
                    remuneration = zip(payments, dates)
                    cleaned_remuneration = self._cleanup_remuneration(remuneration)

                    entry = {
                        "interest": interest_name,
                        "remuneration": cleaned_remuneration,
                        "raw_record": full_record
                    }

                    self._logger.debug(" ---> interest: %s" % interest_name)
                    self._logger.debug(" ---> remuneration_clean: %s\n\n" % cleaned_remuneration)
                    # self._logger.debug(" ---> full record: %s" % full_record)

                    records.append(entry)
                else:
                    self._logger.debug("######## %s" % record)
                self._logger.debug("-")
        return records

    def _parse_travel_record(self, data):

        # this interest record follows the following format:
        # record[0] = interest name
        # record[2] = remuneration
        # record[3] = destination
        # record[4] = visit dates
        # record[5] = purpose
        # record[6] = date interest was registered

        records = []
        for record in data["records"]:
            full_record = u"\n".join([item for item in record])
            interest_name, amount, destination = None, None, None
            visit_dates, purpose, registered = None, None, None
            if len(record) == 7:
                interest_name = self.resolver.find_influencer(record[0])
                if not interest_name:
                    interest_name = self._split_if_colon(record[0])
                amount = [y for x, y in self._find_money(record[2])]
                destination = self.resolver.get_entities(record[3])
                visit_dates = self._split_if_colon(record[4])
                purpose = self._split_if_colon(record[5])
                registered = self._find_dates(record[6])
            elif len(record) != 7:
                # this interest record is typically 7 lines but there are exceptions
                # parse each line for interest details when this is the case
                for item in record:
                    if "Name of donor" in item:
                        interest_name = self.resolver.find_influencer(record[0])
                        if not interest_name:
                            interest_name = self._split_if_colon(record[0])
                    elif "Amount of donation" in item:
                        amount = [y for x, y in self._find_money(item)]
                    elif "Destination of visit" in item:
                        destination = self.resolver.get_entities(item)
                    elif "Date of visit" in item:
                        visit_dates = self._split_if_colon(item)
                    elif "Purpose of visit" in item:
                        purpose = self._split_if_colon(item)
                    elif "Registered" in item:
                        registered = self._find_dates(item)

            entry = {
                "interest": interest_name,
                "remuneration": amount,
                "purpose": purpose,
                "vist_dates": visit_dates,
                "registered": registered,
                "raw_record": full_record
            }

            self._logger.debug(" ---> interest: %s" % interest_name)
            self._logger.debug(" ---> dest/cost: %s %s" % (destination, amount))
            self._logger.debug(" ---> registered: %s" % registered)
            self._logger.debug("-")

            records.append(entry)
        return records

    def _parse_unstructured_record(self, data):

        # this interest record has interest information on every line
        # record[0] may have the Clients category exception

        records = []
        for record in data["records"]:
            for item in record:
                interest_name = None
                
                # record[0] may not contain interest data
                # e.g. in the Clients category members with multiple
                # directorships will entry which company the interests
                # are clients of.
                
                if "(of " == item[:4].lower() or "of " == item[:3].lower():
                    continue
                else:
                    interest_name = self.resolver.find_influencer(item)
                    dates = self._find_dates(item)
                    if interest_name:
                        # if no interest is found, skip record
                        entry = {
                            "interest": interest_name,
                            "registered": dates,
                            "raw_record": item
                        }
                        self._logger.debug(" ---> interest: %s" % interest_name)
                        self._logger.debug(" ---> registered: %s" % dates)

                        records.append(entry)
        return records

    def _parse_sponsorships(self, data):

        # this interest record follows the following format:
        # record[0] = interest name
        # record[2] = remuneration & nature of gift
        # record[3] = donor status
        # record[4] = date interest was registered

        records = []
        for record in data["records"]:
            full_record = u"\n".join([item for item in record])
            interest_name, amount = None, None
            donor_status, registered = None, None
            if len(record) == 1:
                continue
            elif len(record) == 5:
                interest_name = self.resolver.find_influencer(record[0])
                if not interest_name and ":" in record[0]:
                    interest_name = self._split_if_colon(record[0])
                amount = [y for x, y in self._find_money(record[2])]
                donor_status = self._split_if_colon(record[3])
                registered = self._find_dates(record[4])
            else:
                for item in record:
                    # this interest record is typically 5 lines but there are exceptions
                    # parse each line for interest details when this is the case
                    if "Name of donor" in item:
                        interest_name = self.resolver.find_influencer(record[0])
                        if not interest_name and ":" in item:
                            interest_name = self._split_if_colon(item)
                    elif "Amount of donation" in item:
                        amount = [y for x, y in self._find_money(record[2])]
                    elif "Donor status" in item:
                        donor_status = self._split_if_colon(item)
                    elif "Registered" in item:
                        registered = self._find_dates(item)

            entry = {
                "interest": interest_name,
                "remuneration": amount,
                "donor_status": donor_status,
                "registered": registered,
                "raw_record": full_record
            }

            self._logger.debug(" ---> interest: %s" % interest_name)
            self._logger.debug(" ---> registered: %s" % registered)

            records.append(entry)
        return records

    def _parse_gifts(self, data):

        # this interest record follows the following format:
        # record[0] = interest name
        # record[2] = remuneration & nature of gift
        # record[3] = date received
        # record[4] = date accepted
        # record[5] = donor status
        # record[6] = date interest was registered

        records = []
        for record in data["records"]:
            interest_name, amount, nature, accepted = None, None, None, None
            donor_status, registered, receipt = None, None, None
            full_record = u"\n".join([item for item in record])
            if len(record) == 7:
                interest_name = self.resolver.find_influencer(record[0])
                if not interest_name and ":" in record[0]:
                    interest_name = self._split_if_colon(record[0])
                amount = [y for x, y in self._find_money(record[2])]
                nature = self._split_if_colon(record[2])
                receipt = self._find_dates(record[3])
                accepted = self._find_dates(record[4])
                donor_status = self._split_if_colon(record[5])
                registered = self._find_dates(record[6])
            else:
                for item in record:
                    # this interest record is typically 7 lines but there are exceptions
                    # parse each line for interest details when this is the case
                    if "Name of donor" in item:
                        interest_name = self.resolver.find_influencer(record[0])
                        if not interest_name and ":" in item:
                            interest_name = self._split_if_colon(item)
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

            entry = {
                "interest": interest_name,
                "remuneration": amount,
                "nature": nature,
                "receipt": receipt,
                "donor_status": donor_status,
                "accepted": accepted,
                "registered": registered,
                "raw_record": full_record
            }

            self._logger.debug(" ---> interest: %s" % interest_name)
            self._logger.debug(" ---> registered: %s" % registered)
            self._logger.debug("-")

            records.append(entry)
        return records

    def _parse_land_ownership(self, data):

        # this interest record has interest information on every line

        records = []
        for record in data["records"]:
            full_record = u"\n".join([item for item in record])
            for item in record:
                locations = self.resolver.get_entities(item)
                if isinstance(locations, list):
                    locations = locations[0]
                dates = self._find_dates(item)
                if locations:
                    self._logger.debug("----> %s %s" % (locations, dates))
                entry = {
                    "interest": locations,
                    "raw_record": full_record
                }
                records.append(entry)
        return records

    def _parse_clients(self, data):

        # client interests one one of two conventions,
        # list records or unstructured records
        # pick the appropriate one based on the full record structure

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

    def _find_dates(self, data):
        dates = re.findall(date_search, data)
        if dates:
            return dates
        else:
            return None

    def _find_money(self, data):
        money = None
        money = re.findall(money_search, data)
        return money

    def _get_mp(self, entry):
        # TODO Veify entity extraction is working as expected
        result = self.resolver.find_mp(entry)
        if not result:
            return entry
        else:
            return result

    def _show_record(self, data):
        self._logger.debug("   * %s" % data["category_name"])
        print data["records"]
        for record in data["records"]:
            for item in record:
                self._logger.debug("     %s" % item)
            self._logger.debug("---")

    def _cleanup_remuneration(self, data):
        money_entry, date_entries = 0, 1
        new_list = []
        if data:
            for entry in data:
                if len(entry[0]) > 0:
                    # self._logger.debug("%s %s" % (entry[0][0][1], entry[1]))
                    if entry[date_entries] and len(entry[date_entries]) > 1:
                        received = entry[date_entries][0]
                        registered = entry[date_entries][1]
                    elif entry[1] and len(entry[1]) == 1:
                            received = "Unknown"
                            registered = entry[date_entries][0]
                    else:
                        received = "Unknown"
                        registered = "Unknown"
                    new_entry = {
                        "amount": entry[money_entry][0][1],
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

    @staticmethod
    def _fix_categories(cat):
        if cat == "Remunerated employment, office, profession, etc_":
            cat = "Remunerated employment, office, profession etc"

        if cat == "Remunerated employment, office, profession etc_":
            cat = "Remunerated employment, office, profession etc"

        if cat == "remunerated employment, office, profession et":
            cat = "Remunerated employment, office, profession etc"

        if cat == "Gifts, benefits and hospitality (UK) Hours: 8 hrs_":
            cat = "Gifts, benefits and hospitality (UK)"
        return cat


def parse(**kwargs):
    ParseMPsInterests(**kwargs).run()