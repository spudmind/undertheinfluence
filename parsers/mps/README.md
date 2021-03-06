Members of Parliament Parser
=============================

This parser fetches the Members of Parliament list from MySociety's [TheyWorkForYou API](http://www.theyworkforyou.com/api/docs/). 

Parsing
-------

parse_mps.py outputs documents to the `mps_parse` collection, of the following form:

```json
{
	"first_name" : "Bridget",
	"last_name" : "Phillipson",
	"full_name" : "Bridget Phillipson",
	"party" : "Labour",
	"terms" : [
		{
			"left_reason" : "general_election",
			"left_house" : "2015-03-30",
			"entered_house" : "2010-05-06",
			"offices_held" : [
				{
					"position" : "Opposition Whip (Commons)"
				},
				{
					"department" : "Speaker's Committee on the Electoral Commission"
				}
			],
			"party" : "Labour",
			"constituency" : "Houghton and Sunderland South"
		}
	],
	"wikipedia_url" : "http://en.wikipedia.org/wiki/Bridget_Phillipson",
	"image" : "http://www.theyworkforyou.com/images/mpsL/24709.jpeg",
	"twfy_id" : "24709",
	"publicwhip_id" : "40323",
	"publicwhip_url" : "http://publicwhip.com/mp.php?mpid=24709",
	"number_of_terms" : 1
}```

The mongo command: `db.mps_parse.findOne()` is helpful for seeing a real example of this.
