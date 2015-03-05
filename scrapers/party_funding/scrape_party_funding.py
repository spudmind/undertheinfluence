# -*- coding: utf-8 -*-
import os.path
import logging
from utils import text_io, mongo


class ScrapePartyFunding:
    def __init__(self):
        self._logger = logging.getLogger('spud')
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.db = mongo.MongoInterface()

    def run(self):
        file_name = os.path.join(self.current_path, self.STORE_DIR, 'ec-export.csv')
        self.csv = text_io.CsvInput()
        self.csv.open(file_name)

        for row in self.csv.all_rows:
            self.extract(row)

    def extract(self, row):
        value = row[15][1:].strip()
        if row[9][:1] == ":":
            company_reg = row[9][1:].strip()
        else:
            company_reg = row[9].strip()
        data = {
            "ec_reference": row[0].strip(),
            "recipient": self.make_utf(row[1].strip()),
            "recipient_type": row[2].strip(),
            "donee_type": row[3].strip(),
            "recd_by": row[4].strip(),
            "6212": row[5].strip(),
            "is_sponsorship": row[6].strip(),
            "donor_name": self.make_utf(row[7].strip()),
            "donor_type": row[8].strip(),
            "company_reg": company_reg,
            "donation_type": row[11].strip(),
            "nature_provision": self.make_utf(row[12].strip()),
            "purpose": self.make_utf(row[13].strip()),
            "value": self.make_utf(value),
            "received_date": row[16].strip(),
            "accepted_date": row[17].strip(),
            "reported_date": row[18].strip(),
        }
        self.print_dic(data)
        self._logger.debug("\n\n")
        self.db.save("party_funding_scrape", data)

    def print_dic(self, dictionary):
        for keys, values in dictionary.items():
            self._logger.debug(" %-20s:%-25s" % (keys, values))

    def make_utf(self, field):
        try:
            return u"{0}".format(field.decode('utf-8', "replace"))
        except UnicodeDecodeError, e:
            self._logger.error("******* %s" % field)

def scrape():
    ScrapePartyFunding().run()
