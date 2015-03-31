Lords Parser
=============

This parser fetches the Members of Parliament list from MySociety's [TheyWorkForYou API](http://www.theyworkforyou.com/api/docs/). 

Parsing
-------

parse_lords.py outputs documents to the `lords_parse` collection, of the following form:

```json
{
	"title" : "Lord",
	"first_name" : "Dominic",
	"last_name" : "Addington",
	"full_name" : "Lord Addington",
	"party" : "Liberal Democrats"
	"terms" : [
		{
			"left_reason" : null,
			"entered_house" : "1982-01-01",
			"constituency" : null,
			"left_house" : null,
			"party" : "Liberal Democrat"
		}
	],
	"image" : null,
	"twfy_id" : "13368",
	"source" : "http://www.theyworkforyou.com/api/docs/getLord?id=13368#output",
}
```

The mongo command: `db.lords_parse.findOne()` is helpful for seeing a real example of this.
