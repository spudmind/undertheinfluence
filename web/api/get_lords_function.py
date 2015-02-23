from utils import mongo
from flask import url_for


class LordsApi:
    def __init__(self):
        self._db = mongo.MongoInterface()
        self._db_table = 'api_lords'

        self._funding = "influences.electoral_commission.donation_total"

    def request(self, **args):
        page = args.get('page', 1)

        query = self._filter_party(args)
        query = self._filter_funding(args, query=query)
        results, response = self._db.query(self._db_table, query=query, page=page)
        if response['has_more']:
            next_query = args
            next_query['page'] = page + 1
            response['next_url'] = url_for('getLords', _external=True, **next_query)

        response["results"] = [{
            "name": entry["name"],
            "party": entry["party"],
            "image_url": None,
            "detail_url": url_for('show_lord', name=entry["name"], _external=True),
            "weight": entry["weight"],
            "twfy_id": entry["twfy_id"],
            "labels": entry["labels"],
            "influences_summary": entry["influences"]
        } for entry in results]

        return response

    def _filter_party(self, args, query={}):
        if args.get("party") is not None:
            query["party"] = args.get("party")
        return query

    def _filter_funding(self, args, query={}):
        _funding_search = {}
        if args.get("donations_gt"):
            _funding_search["$gt"] = args.get("donations_gt")
        if args.get("donations_lt"):
            _funding_search["$lt"] = args.get("donations_lt")
        if _funding_search != {}:
            query[self._funding] = _funding_search
        return query
