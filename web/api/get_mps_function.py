from web.api import BaseAPI
from flask import url_for
from utils import mongo


class MpsApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_mps'

        self._remuneration = "influences.register_of_interests.remuneration_total"
        self._funding = "influences.electoral_commision.donation_total"

    def request(self, **args):
        page = args.get('page', 1)

        query = self._filter_party(args)
        query = self._filter_interests(args, query=query)
        query = self._filter_funding(args, query=query)
        results, response = self._db.query(self._db_table, query=query, page=page)
        if response['has_more']:
            next_query = args
            next_query['page'] = page + 1
            response['next_url'] = url_for('getMps', _external=True, **next_query)

        response["results"] = [
            {
                "name": entry["name"],
                "party": entry["party"],
                "image_url": entry["image_url"],
                #"detail_url": url_for('show_mp', name=entry["name"], _external=True),
                "detail_url": self.named_entity_resources(
                    entry["name"], entry["labels"]
                )[0],
                "weight": entry["weight"],
                "twfy_id": entry["twfy_id"],
                "labels": entry["labels"],
                "government_positions": entry["government_positions"],
                "influences_summary": entry["influences"]
            }
            for entry in results
        ]

        return response

    def _filter_party(self, args, query={}):
        if args.get("party") is not None:
            query["party"] = args.get("party")
        return query

    def _filter_interests(self, args, query={}):
        _remuneration_search = {}
        if args.get("interests_gt"):
            _remuneration_search["$gt"] = args.get("interests_gt")
        if args.get("interests_lt"):
            _remuneration_search["$lt"] = args.get("interests_lt")
        if _remuneration_search != {}:
            query[self._remuneration] = _remuneration_search
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

