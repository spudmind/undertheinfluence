# -*- coding: utf-8 -*-
import calendar
from datetime import datetime
import re


class FuzzyDate():
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
            date = datetime.strptime("-".join(date_match.groups()), "%b-%Y")
            return date, date_match.start()

        date_match = re.search(r"(\d{2})/(\d{2})/(\d{2})", text)
        if date_match:
            date = datetime.strptime("-".join(date_match.groups()), "%d-%m-%y")
            return date, date_match.start()

def extract_date_range(text):
    f = FuzzyDate()
    start = f.extract_date(text)
    if start is None:
        return None
    end = FuzzyDate().extract_date(text[start[1] + 1:])
    if end is None:
        return None

    # set the day to the end of the month
    start = start[0]
    end = end[0]
    end_day = calendar.monthrange(end.year, end.month)[1]
    end = end.replace(day=end_day)
    return str(start.date()), str(end.date())

def extract_date(text):
    d = FuzzyDate().extract_date(text)
    if d:
        return str(d[0].date())

def parse_date(text):
    return FuzzyDate().parse_date(text)
