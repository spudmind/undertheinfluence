# -*- coding: utf-8 -*-
import os.path
import logging
import mechanize


class FetchPartyFunding:
    def __init__(self):
        self._logger = logging.getLogger('spud')
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))

    def run(self):
        file_name = os.path.join(self.current_path, self.STORE_DIR, 'ec-export.csv')
        if not os.path.exists(file_name):
            self.fetch(file_name)

    def fetch(self, file_name):
        br = mechanize.Browser()
        # load the search page
        _ = br.open("https://pefonline.electoralcommission.org.uk/Search/SearchIntro.aspx")
        br.select_form(name="aspnetForm")
        # click to view "Basic donation search"
        _ = br.submit(name="ctl00$ctl05$ctl01")
        br.select_form(name="aspnetForm")
        # click to export results to CSV file
        csv_gen = br.submit(name="ctl00$ContentPlaceHolder1$searchControl1$btnExportAllResults")
        with open(file_name, 'w') as f:
            for csv_line in csv_gen:
                f.write(csv_line)

def fetch():
    FetchPartyFunding().run()
