# -*- coding: utf-8 -*-
import calendar
from datetime import datetime
import re


class FuzzyDate:
    def __init__(self, date=None, index=None, text=None, date_format=None):
        self.date = date
        self.index = index
        self.text = text
        self.date_format = date_format

    def __str__(self):
        return str(self.date)

    def __repr__(self):
        return "<FuzzyDate %s>" % str(self)

def parse_date(date_text, date_format=None, date_range=None):
    # first, if we have a format, try simply parsing
    if date_format:
        try:
            date = datetime.strptime(date_text, date_format).date()
            return FuzzyDate(date=date, text=date_text, date_format=date_format)
        except ValueError:
            pass

    # specify some directives to try
    directives = {
        # e.g. "Oct", "October", "10"
        "month": ("%b", "%B", "%m"),
        # e.g. "14", "2014", "014"
        "year": ("%y", "%Y", "0%y"),
    }

    # get the separators
    separators = re.findall(r"[^a-zA-Z0-9]+", date_text)
    # date should have two or three parts
    if len(separators) > 2:
        return

    if len(separators) == 0:
        if date_range:
            if date_text == "Sept":
                date_text = "Sep"
            for month_format in directives["month"]:
                try:
                    date = datetime.strptime(date_text, month_format).date()
                    date = date.replace(day=1, year=date_range[0].date.year)
                    # while we're still below the upper bound
                    while date <= date_range[1].date:
                        if date < date_range[0].date:
                            # if the current date is below the lower bound, add a year
                            date = date.replace(year=date.year+1)
                        else:
                            # otherwise we're inside the bounds, so return
                            return FuzzyDate(date=date, text=date_text)
                except ValueError:
                    pass
        return


    if len(separators) == 1:
        date_format_base = ""
    elif len(separators) == 2:
        date_format_base = "%%d%s" % separators.pop(0)

    for month in directives["month"]:
        for year in directives["year"]:
            try:
                date_format = "%s%s%s%s" % (date_format_base, month, separators[0], year)
                date = datetime.strptime(date_text, date_format).date()
                return FuzzyDate(date=date, text=date_text, date_format=date_format)
            except ValueError:
                pass

# Extract date from string
def extract_date(text):
    # e.g. Jan 2010
    date_match = re.search(r"(%s).*?(\d{4})" % "|".join(calendar.month_abbr[1:]), text)
    if date_match:
        date = datetime.strptime("-".join(date_match.groups()), "%b-%Y").date()
        return FuzzyDate(date=date, index=date_match.start(), text=text)

    date_match = re.search(r"(\d{2})/(\d{2})/(\d{2})", text)
    if date_match:
        date = datetime.strptime("-".join(date_match.groups()), "%d-%m-%y").date()
        return FuzzyDate(date=date, index=date_match.start(), text=text)

def extract_date_range(text):
    start = extract_date(text)
    if start is None:
        return None
    end = extract_date(text[start.index + 1:])
    if end is None:
        return None

    # set the day to the end of the month
    end_day = calendar.monthrange(end.date.year, end.date.month)[1]
    end.date = end.date.replace(day=end_day)
    return (start, end)

# def extract_date(text):
#     d = FuzzyDate().extract_date(text)
#     if d:
#         return str(d[0].date())

# def parse_date(text):
#     return FuzzyDate().parse_date(text)
