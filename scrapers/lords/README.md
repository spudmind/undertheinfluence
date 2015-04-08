Lords Scraper
=============

This “scraper” pulls data from [the TheyWorkForYou API](http://www.theyworkforyou.com/api/). It’s not really a scraper, since that data is already machine-readable.

Fetching
--------

fetch_lords.py outputs documents to the `lords_fetch` collection, of the following form:

```json
{
    "filename": "relative link to the fetched json file",
    "source": {
        "url": "URL of the documentation page for the relevant record",
        "linked_from_url": "URL of the documentation page for the index",
        "fetched": "Timestamp when the json document was fetched"
    }
}
```

The mongo command: `db.lords_fetch.findOne()` is helpful for seeing a real example of this.

Scraping
--------

scrape_lords.py outputs documents to the `lords_scrape` collection, of the following form:

```json
{
    "title": "e.g. Lord / Baron / Bishop / Viscount etc",
    "name": "Name of the Lord",
    "aliases": ["Alternative names, including formal title"],
    "party": "Affiliated party, or Crossbench / Bishop",
    "twfy_id": "TheyWorkForYou person ID",
    "image": "URL to a photo of the lord, or null if one isn't available",
    "terms": [{
        "entered_house": "YYYY-MM-DD",
        "left_house": "YYYY-MM-DD",
        "left_reason": "e.g. changed_party",
        "constituency": "Constituency name for the term, or null",
        "party": "Affiliated party for the term, or Crossbench / Bishop"
    }],
    "source": {
        "...": "As described for the lords_fetch json above"
    }
}
```
