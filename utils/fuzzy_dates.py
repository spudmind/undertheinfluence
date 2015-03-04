# -*- coding: utf-8 -*-
import calendar
from datetime import datetime
import re

class FuzzyDate():
    def __init__(self):
        self.date = None

    def parse_date(self, date_text):
        # specify some directives to try
        directives = {
            "month": ("%b", "%B", "%m"),
            "year": ("%y", "%Y", "0%y"),
        }

        # get the separators
        separators = re.findall(r"[^a-zA-Z0-9]+", date_text)
        # date should have two or three parts
        if len(separators) < 1 or len(separators) > 2:
            return
        if len(separators) == 2:
            date_format_base = "%%d%s" % separators.pop(0)
        else:
            date_format_base = ""

        for month in directives["month"]:
            for year in directives["year"]:
                try:
                    date_format = "%s%s%s%s" % (date_format_base, month, separators[0], year)
                    _ = datetime.strptime(date_text, date_format)
                    return date_format
                except ValueError:
                    pass

    def extract_date(self, text):
        # e.g. Jan 2010
        date_match = re.search(r"(%s).*?(\d{4})" % "|".join(calendar.month_abbr[1:]), text)
        if date_match:
            self.start = date_match.start()
            self.date = datetime.strptime("-".join(date_match.groups()), "%b-%Y")
            return self

        date_match = re.search(r"\d{2}/(\d{2})/(\d{2})", text)
        if date_match:
            self.start = date_match.start()
            self.date = datetime.strptime("-".join(date_match.groups()), "%m-%y")
            return self

        date_match = re.search(r"\d{2}/(\d{2})/(\d{2})", text)
        if date_match:
            self.start = date_match.start()
            self.date = datetime.strptime("-".join(date_match.groups()), "%m-%y")
            return self

        date_match = re.search(r"\d{2}/(\d{2})/(\d{2})", text)
        if date_match:
            self.start = date_match.start()
            self.date = datetime.strptime("-".join(date_match.groups()), "%m-%y")
            return self

def extract_date_range(text):
    start = FuzzyDate().extract_date(text)
    if start is None:
        return None
    end = FuzzyDate().extract_date(text[start.start + 1:])
    if end is None:
        return None
    return start.date, end.date

def extract_date(text):
    f = FuzzyDate().extract_date(text)
    if f:
        return f.date

def parse_date(text):
    return FuzzyDate().parse_date(text)
