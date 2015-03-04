from web.api import BaseAPI
from flask import url_for
from utils import mongo


class PoliticiansApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_politicians'
        self.query = {}

        self._remuneration = "influences.register_of_interests.remuneration_total"
        self._funding = "influences.electoral_commision.donation_total"

    def request(self, **args):
        pager = {}
        page = args.get('page', 1)

        print "api args:", args

        self._filter_party(args)
        self._filter_type(args)
        self._filter_interests(args)
        self._filter_funding(args)
        self._filter_office(args)

        print "api query:", self.query

        results, response = self._db.query(self._db_table, query=self.query, page=page)
        if response['has_more']:
            next_query = args
            next_query['page'] = page + 1
            print "next args:", next_query
            response['next_url'] = url_for('GetPoliticians', _external=True, **next_query)
            pager["next"] = url_for('show_politicians', _external=True, **next_query)
        if page > 1:
            previous_query = args
            previous_query['page'] = page - 1
            pager["previous"] = url_for('show_politicians', _external=True, **previous_query)

        response['pager'] = pager
        response["results"] = [
            {
                "name": entry["name"],
                "party": entry["party"],
                "image_url": entry["image_url"],
                #"detail_url": url_for('show_mp', name=entry["name"], _external=True),
                "detail_url": self.named_entity_resources(
                    entry["name"], entry["labels"]
                )[0],
                "party_url": self.named_entity_resources(
                    entry["party"], "Political Party"
                )[0],
                "weight": entry["weight"],
                "twfy_id": entry["twfy_id"],
                "labels": entry["labels"],
                "government_positions": entry["government_positions"],
                "government_departments": entry["government_departments"],
                "influences_summary": entry["influences"],
                "type": entry["type"]
            }
            for entry in results
        ]

        return response

    def _filter_party(self, args):
        if args.get("party") is not None:
            self.query["party"] = args.get("party")

    def _filter_type(self, args):
        if args.get("type") is not None:
            self.query["type"] = args.get("type")

    def _filter_interests(self, args):
        _remuneration_search = {}
        if args.get("interests_gt"):
            _remuneration_search["$gt"] = args.get("interests_gt")
        if args.get("interests_lt"):
            _remuneration_search["$lt"] = args.get("interests_lt")
        if _remuneration_search != {}:
            self.query[self._remuneration] = _remuneration_search

    def _filter_funding(self, args):
        _funding_search = {}
        if args.get("donations_gt"):
            _funding_search["$gt"] = args.get("donations_gt")
        if args.get("donations_lt"):
            _funding_search["$lt"] = args.get("donations_lt")
        if _funding_search != {}:
            self.query[self._funding] = _funding_search

    def _filter_office(self, args):
        if args.get("government_office"):
            self.query["$and"] = [
                {
                    "government_departments": {
                    "$in": [args.get("government_office")]}
                }
            ]

