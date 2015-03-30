Members of Parliament Parser
=============================

This parser fetches the Members of Parliament list from MySociety's [TheyWorkForYou API](http://www.theyworkforyou.com/api/docs/). 

Parsing
-------

fetch_mps.py outputs documents to the `mps_fetch` collection, of the following form:

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

The mongo command: `db.mps_fetch.findOne()` is helpful for seeing a real example of this.
