# -*- coding: utf-8 -*-
import calendar
import csv
from datetime import datetime
import logging
import os.path
import re
import webbrowser
from utils import mongo, fuzzy_dates


class ScrapeMeetings():
    def __init__(self):
        # fetch the logger
        self._logger = logging.getLogger("spud")
        # database stuff
        self.db = mongo.MongoInterface()
        # local directory to save fetched files to
        self.STORE_DIR = "store"
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))

    def find_header_rows(self, meetings):
        found_headers = []
        headers_re = [
            ("date", re.compile(r"(?:date|month)", re.IGNORECASE)),
            ("organisation", re.compile(r"(?:organisation|individuals|senior executive)", re.IGNORECASE)),
            ("name", re.compile(r"(?:name|minister|officials|spad)", re.IGNORECASE)),
            ("purpose", re.compile(r"(?:purpose|nature|issues)", re.IGNORECASE)),
        ]

        for row_idx, row in enumerate(meetings):
            column_mappings = {}
            # create a copy
            current_headers = list(headers_re)
            for column_idx, cell in enumerate(row):
                for idx, header in enumerate(current_headers):
                    header_id, header_re = header
                    if header_re.search(cell):
                        # remove from the possible headers
                        column_mappings[header_id] = column_idx
                        current_headers.pop(idx)
                        break

            found_header = column_mappings.keys()
            if "date" in found_header and "organisation" in found_header:
                if "name" not in found_header and 0 not in column_mappings.values():
                    # take a guess that the first column is the name
                    column_mappings["name"] = 0
                    found_headers.append((row_idx, column_mappings))

        return found_headers

    def extract_dates_from_title(self, title):
        date_range = fuzzy_dates.extract_date_range(title)
        if date_range:
            start, end = date_range
            # set the day to the end of the month
            end_day = calendar.monthrange(end.year, end.month)[1]
            end = end.replace(day=end_day)

    def read_csv(self, filename):
        full_path = os.path.join(self.current_path, self.STORE_DIR, filename)
        with open(full_path, "rU") as csv_file:
            csv_doc = csv.reader(csv_file, strict=True)
            # read the whole csv in
            return [[cell.strip() for cell in row] for row in csv_doc]

    # strip empty columns; standardize row length
    def normalise_csv(self, meetings):
        row_length = max([len(row) for row in meetings])

        not_empty = {}
        for row in meetings:
            if len(not_empty) == row_length:
                break
            for idx, cell in enumerate(row):
                if idx in not_empty:
                    continue
                if cell != "":
                    not_empty[idx] = None

        not_empty = not_empty.keys()
        return [[m[idx] if idx < len(m) else "" for idx in not_empty] for m in meetings]

    # often, a cell is left blank to mean its value is
    # the same as the value of the cell above. This function populates
    # these blank cells.
    def populate_empty_cells(self, meetings, header_mappings):
        if len(meetings) <= 1:
            return meetings

        pop_meetings = [meetings[0]]
        for idx, row in enumerate(meetings[1:]):
            pop_meeting = {k: row.get(k) if row.get(k) is not None else pop_meetings[idx-1].get(k, "") for k in header_mappings.keys()}
            pop_meetings.append(pop_meeting)

        return pop_meetings

    def csv_to_dicts(self, meeting_rows, header_mappings):
        meeting_dicts = []
        for meeting_row in meeting_rows:
            meeting = {}
            for k, v in header_mappings.items():
                val = meeting_row[v]
                if val == "":
                    continue
                meeting[k] = val
            # we avoid adding blank rows
            if meeting != {}:
                meeting_dicts.append(meeting)
        return meeting_dicts

    def parse_meetings(self, meetings):
        date_format = ""
        for meeting in meetings:
            if "date" not in meeting:
                continue
            try:
                meeting["date"] = datetime.strptime(meeting["date"], date_format)
            except ValueError:
                date_format = fuzzy_dates.parse_date(meeting["date"])
                if date_format is None:
                    date_format = ""
                else:
                    meeting["date"] = datetime.strptime(meeting["date"], date_format)
        return meetings

    def scrape_csv(self, meta):
        meetings = self.read_csv(meta["filename"])
        meetings = self.normalise_csv(meetings)
        header_rows = self.find_header_rows(meetings)
        if header_rows == []:
            return []
        meetings_dicts = []
        for idx, header_row in enumerate(header_rows):
            if idx == len(header_rows) - 1:
                meetings_block = meetings[header_row[0]+1:]
            else:
                meetings_block = meetings[header_row[0]+1:header_rows[idx + 1][0]-1]
            block_dicts = self.csv_to_dicts(meetings_block, header_row[1])
            block_dicts = self.populate_empty_cells(block_dicts, header_row[1])
            meetings_dicts += block_dicts
            if "name" not in header_row[1]:
                webbrowser.open(meta["url"] + "/preview")
                print meta
                for x in block_dicts:
                    print x
                raw_input()
        return meetings_dicts

    def run(self):
        page = 1
        while True:
            not_scraped, meta = self.db.query("meetings_fetch", {"scraped": False}, page=page)
            if not_scraped == []:
                # we've finished scraping
                break
            for meta in not_scraped:
                if meta["file_type"] == "CSV":
                    meetings = self.scrape_csv(meta)
                    meetings = self.parse_meetings(meetings)
                elif meta["file_type"] == "PDF":
                    # TODO: Parse PDF
                    pass
            page += 1
        for meeting in meetings:
            # self.db.save("meetings_scrape", meeting)
            pass

def scrape():
    ScrapeMeetings().run()
