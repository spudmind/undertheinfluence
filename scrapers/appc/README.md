APPC Scraper
============

This scraper fetches data from [the current APPC register](http://www.appc.org.uk/members/register/), as well as [previous registers](http://www.appc.org.uk/previous-registers/). For the timebeing, it only scrapes the current register. At some point, we'll make it scrape the previous registers it has fetched.

Fetching
--------

fetch_appc.py outputs documents to the `appc_fetch` collection, of the following form:

```json
{
    "filename": "relative link to the fetched file - either HTML or PDF",
    "date_range": ["YYYY-MM-DD", "YYYY-MM-DD"],
    "source": {
        "url": "Source URL. For the HTML, this is null because there is no direct link (it requires a POST request)",
        "linked_from_url": "Index page URL, from which the source documents are linked",
        "fetched": "Timestamp when the document (HTML or PDF) was fetched"
    }
}
```

The mongo command: `db.appc_fetch.findOne()` is helpful for seeing a real example of this.

Scraping
--------

scrape_appc.py outputs documents to the `appc_scrape` collection, of the following form:

```json
{
    "name": "Name of the lobbying organisation",
    "date_range": ["YYYY-MM-DD", "YYYY-MM-DD"],
    "addresses": [
        ["List of lists of addresses", "The next list gives an example of the sort of format"],
        ["e.g.:", "Address line 1", "Address line 2", "City", "Postcode"]
    ],
    "contacts": [
        ["List of lists of contact information", "There's usually just one, but occasionally more"]
    ],
    "countries": ["List of countries that the organisation works in"],
    "staff": {
        "has_pass": ["List of names of staff members who have a parliamentary pass"],
        "no_pass": ["List of names of all other staff members"]
    },
    "clients": {
        "name": "Name of the client organisation",
        "description": "Further information about the client organisation. Format varies; this is often just a URL, but occasionally other info."
    },
    "source": {
        "url": "Source URL, as described above",
        "linked_from_url": "Index page URL, as described above",
        "fetched": "Timestamp, as described above"
    }
}
```
