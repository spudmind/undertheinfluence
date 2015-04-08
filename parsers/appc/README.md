APPC Parser
===========

This scraper fetches data from [the current APPC register](http://www.appc.org.uk/members/register/), as well as [previous registers](http://www.appc.org.uk/previous-registers/). For the timebeing, it only scrapes the current register. At some point, we'll make it scrape the previous registers it has fetched.

Parsing
-------

parse_appc.py outputs documents to the `appc_parse` collection, of the following form:

```json
{
    "name" : "Access Partnership",
    "address" : "Broadway Studios\n20 Hammersmith Broadway\nLondon\nW6 7AF",   
	"contact_details" : "Gregory Francis\n020 8600 0630\ngreg@accesspartnership.com\nwww.accesspartnership.com",
	"pa_contact" : null,
	"date_range" : [
		"2014-12-01",
		"2015-02-28"
	],
	"clients" : [
		{
			"client_type" : "consultancy",
			"name" : "Government of Bermuda",
			"description" : null
		},
		{
			"client_type" : "consultancy",
			"name" : "Salesforce.com",
			"description" : null
		}
	],
	"staff" : [
		{
			"staff_type" : "no_pass",
			"name" : "Matthew Allison"
		},
		{
			"staff_type" : "no_pass",
			"name" : "Matthew McDermott"
		},
		{
			"staff_type" : "no_pass",
			"name" : "Laura Sallstrom"
		}
	],
	"countries" : [
		"Belgium",
		"United Arab Emirates",
		"United States"
	],
	"source" : {
		"url" : null,
		"linked_from_url" : "http://www.appc.org.uk/members/register/",
		"fetched" : "2015-03-31 16:43:37.127169"
	},
}
```

The mongo command: `db.appc_parse.findOne()` is helpful for seeing a real example of this.
