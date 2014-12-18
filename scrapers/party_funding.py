# -*- coding: utf-8 -*-
import os

from utils import text_io, mongo


current_path = os.path.dirname(os.path.abspath(__file__))


class PartyFundingScaper:
    def __init__(self):
        self.csv = text_io.CsvInput()
        self.file_name = current_path + '/data/EC-Export-20141215-1737.csv'
        self.csv.open(self.file_name)
        self.cache = mongo.MongoInterface()

    def run(self):
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
            "value": value,
            "received_date": row[16].strip(),
            "accepted_date": row[17].strip(),
            "reported_date": row[18].strip()
        }
        self.print_dic(data)
        print "\n\n"
        self.cache.db.scraped_party_funding.save(data)

    @staticmethod
    def print_dic(dictionary):
        for keys, values in dictionary.items():
            print " %-20s:%-25s" % (keys, values)

    @staticmethod
    def make_utf(field):
        try:
            return u"{0}".format(field.decode('utf-8', "replace"))
        except UnicodeDecodeError, e:
            print "*******", field
