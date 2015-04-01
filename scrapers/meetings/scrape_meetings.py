# -*- coding: utf-8 -*-
import calendar
from datetime import datetime
import logging
import os.path
import re
import webbrowser
from utils import mongo, fuzzy_dates, unicode_csv


class ScrapeMeetings:
    def __init__(self, **kwargs):
        # fetch the logger
        self._logger = logging.getLogger("spud")
        # database stuff
        self.db = mongo.MongoInterface()
        self.PREFIX = "meetings"
        if kwargs["refreshdb"]:
            self.db.drop("%s_scrape" % self.PREFIX)
        # get the current path
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.STORE_DIR = "store"

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

    def read_csv(self, filename):
        full_path = os.path.join(self.current_path, self.STORE_DIR, filename)
        with open(full_path, "rU") as csv_file:
            csv = unicode_csv.UnicodeReader(csv_file, encoding="latin1", strict=True)
            # read in the whole csv
            return [[cell.strip() for cell in row] for row in csv]

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
            pop_meeting = {k: row.get(k) if row.get(k) is not None else pop_meetings[idx].get(k, "") for k in header_mappings.keys()}
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

    def parse_meetings(self, meetings, meta):
        date_format = None
        date_range = fuzzy_dates.extract_date_range(meta["title"])
        # print meta
        # for x in meetings:
        #     print x
        # webbrowser.open(meta["source"]["url"] + "/preview")
        # raw_input()

        for meeting in meetings:
            if "date" not in meeting:
                self._logger.warning("Date missing from the following row:", meeting)
                continue
            meeting_date = fuzzy_dates.parse_date(meeting["date"], date_format=date_format, date_range=date_range)
            if meeting_date:
                meeting["date"] = str(meeting_date.date)
                date_format = meeting_date.date_format
            else:
                self._logger.warning("Couldn't find '%s' in range %s" % (meeting["date"], date_range))
        return meetings

    def scrape_csv(self, meta):
        self._logger.info("... %s" % meta["filename"])
        meetings = self.read_csv(meta["filename"])
        meetings = self.normalise_csv(meetings)
        # find index(es) of header rows
        header_rows = self.find_header_rows(meetings)
        if header_rows == []:
            # doesn't look like this file contains meeting data
            return []
        meetings_dicts = []
        # sometimes a file contains multiple groups of meetings
        for idx, header_row in enumerate(header_rows):
            if idx == len(header_rows) - 1:
                meetings_block = meetings[header_row[0]+1:]
            else:
                meetings_block = meetings[header_row[0]+1:header_rows[idx + 1][0]-1]
            block_dicts = self.csv_to_dicts(meetings_block, header_row[1])
            block_dicts = self.populate_empty_cells(block_dicts, header_row[1])

            meetings_dicts += block_dicts
            # if "name" not in header_row[1]:
        return meetings_dicts

    def run(self):
        self._logger.info("Scraping Meetings")
        _all_meetings = self.db.fetch_all("%s_fetch" % self.PREFIX, paged=False)
        for meta in _all_meetings:
            meetings = []
            meta["published_at"] = str(datetime.strptime(meta["published_at"], "%d %B %Y").date())
            if meta["file_type"] == "CSV":
                meetings = self.scrape_csv(meta)
                meetings = self.parse_meetings(meetings)
            elif meta["file_type"] == "PDF":
                # TODO: Parse PDF
                pass

            for meeting in meetings:
                for k in ["published_at", "department", "title", "source"]:
                    meeting[k] = meta[k]
                self.db.save("%s_scrape" % self.PREFIX, meeting)


def scrape(**kwargs):
    ScrapeMeetings(**kwargs).run()
