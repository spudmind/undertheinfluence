# -*- coding: utf-8 -*-
import os.path
import logging

import mechanize

from utils import text_io, mongo


current_path = os.path.dirname(os.path.abspath(__file__))


class PartyFundingScraper:
    def __init__(self):
        self._logger = logging.getLogger('spud')

    def run(self):
        file_name = os.path.join(current_path, 'data', 'EC-Export.csv')
        if not os.path.exists(file_name):
            self.scrape(file_name)
        self.csv = text_io.CsvInput()
        self.csv.open(file_name)
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.scraped_party_funding

        for row in self.csv.all_rows:
            self.extract(row)

    def scrape(self, file_name):
        br = mechanize.Browser()
        # load the search page
        _ = br.open("https://pefonline.electoralcommission.org.uk/Search/SearchIntro.aspx")
        br.select_form(name="aspnetForm")
        # click to view "Basic donation search"
        _ = br.submit(name="ctl00$ctl05$ctl01")
        br.select_form(name="aspnetForm")
        # click to export results to CSV file
        csv_gen = br.submit(name="ctl00$ContentPlaceHolder1$searchControl1$btnExportAllResults")
        with open(file_name, 'w+') as f:
            for csv_line in csv_gen:
                f.write(csv_line)

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
            "reported_date": row[18].strip()
        }
        self.print_dic(data)
        self._logger.debug("\n\n")
        self.cache_data.save(data)

    def print_dic(self, dictionary):
        for keys, values in dictionary.items():
            self._logger.debug(" %-20s:%-25s" % (keys, values))

    @staticmethod
    def make_utf(field):
        try:
            return u"{0}".format(field.decode('utf-8', "replace"))
        except UnicodeDecodeError, e:
            self._logger.error("******* %s" % field)
