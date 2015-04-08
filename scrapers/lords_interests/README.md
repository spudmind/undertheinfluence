Lords Interests Scraper
=======================

This scraper fetches data from [The Lords register of interests](http://data.parliament.uk/membersdataplatform/services/mnis/members), available from the members' data platform.

Fetching
--------

fetch_lords_interests.py outputs JSON files to the `store` directory. These contain records grouped by the date that an individual entered the house of Lords. Where an individual took their seat multiple times, they will appear in these files multiple times.

Documents output to the `lords_interests_fetch` collection are of the following form:

```json
{
    "filename": "relative link to the fetched JSON file",
    "date_range": "a list containing the start date and end date",
    "source": {
        "url": url,
        "linked_from_url": None,
        "fetched": fetched,
    }
}
```
