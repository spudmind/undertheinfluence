# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import os.path
import re
from utils import unicode_csv, mongo


class ScrapePartyFunding:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('spud')
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        # database stuff
        self.db = mongo.MongoInterface()
        self.PREFIX = "party_funding"
        if kwargs["refreshdb"]:
            self.db.drop("%s_scrape" % self.PREFIX)

    def run(self):
        self._logger.info("Scraping Electoral Commission party funding data ...")
        metas = self.db.fetch_all("%s_fetch" % self.PREFIX, paged=False)
        for meta in metas:
            self.extract(meta)
        self._logger.info("Done scraping party funding data.")

    def extract(self, meta):
        with open(os.path.join(self.current_path, meta["filename"]), "r") as f:
            csv = unicode_csv.UnicodeReader(f, encoding="cp1252")
            # make a list of headers
            headers = [re.sub(r"[^a-z0-9 ]", u"", x.lower()).replace(u" ", u"_") for x in csv.next()]
            for row in csv:
                dict_row = dict(zip(headers, [x.strip() for x in row]))
                donation = self.extract_donation(dict_row)
                donation["source"] = meta["source"]
                self.db.save("%s_scrape" % self.PREFIX, donation)
                # # We don't use update here because it's too slow
                # spec = {"name": agency["name"], "date_range": agency["date_range"]}
                # self.db.update("%s_scrape" % self.PREFIX, spec, agency, upsert=True)

    def extract_donation(self, row):
        # this is possibly a bit dodgy... Remove all characters that are
        # neither a number nor a decimal point
        row["value"] = re.sub(r"[^0-9\.]", u"", row["value"])

        if row["company_reg_no"].startswith(":"):
            row["company_reg_no"] = row["company_reg_no"][1:]

        donation = {
            "ec_reference": row["ec_reference"],
            "recipient": row["entity_name"],
            "recipient_type": row["entity_type"],
            "donee_type": row["regulated_donee_type"],
            "recd_by": row["recd_by_au"],
            "6212": row["reported_under_6212"],
            "is_sponsorship": row["is_sponsorship"],
            "donor_name": row["donor_name"],
            "donor_type": row["donor_type"],
            "company_reg": row["company_reg_no"],
            "donation_type": row["type_of_donation"],
            "nature_provision": row["nature__provision"],
            "purpose": row["purpose"],
            "value": row["value"],
            "received_date": self.format_date(row["received_date"]),
            "accepted_date": self.format_date(row["accepted_date"]),
            "reported_date": self.format_date(row["reported_date"]),
        }
        self.print_dic(donation)
        return donation

    # convert %d/%m/%Y to %Y-%m-%d
    @staticmethod
    def format_date(date):
        if date == "":
            return
        return "%s-%s-%s" % (date[6:], date[3:5], date[0:2])
        # return str(datetime.strptime(date, "%d/%m/%Y").date())

    def print_dic(self, dictionary):
        for keys, values in dictionary.items():
            self._logger.debug(" %-20s:%-25s" % (keys, values))
        self._logger.debug("\n\n")


def scrape(**kwargs):
    ScrapePartyFunding(**kwargs).run()
