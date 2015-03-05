from web.api import BaseAPI
from utils import mongo
from flask import url_for


class InfluencersApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_influencers'

        self._remuneration = "influences.register_of_interests.remuneration_total"
        self._funding = "influences.electoral_commision.donation_total"

    def request(self, **args):
        page = args.get('page', 1)

        query = self._filter_labels(args, {})
        query = self._filter_interests(args, query)
        query = self._filter_funding(args, query)

        print query

        results, response = self._db.query(self._db_table, query=query, page=page)
        if response['has_more']:
            next_query = args
            next_query['page'] = page + 1
            response['next_url'] = url_for('getInfluencers', _external=True, **next_query)

        response["results"] = [{
            "name": entry["name"],
            "image_url": None,
            "influences_summary": entry["influences"],
            "labels": entry["labels"],
            "weight": entry["weight"],
            "donor_type": entry["donor_type"],
            "detail_url": self.named_entity_resources(
                entry["name"], entry["labels"]
            )[0]
        } for entry in results]

        return response

    def _filter_labels(self, args, query={}):
        if args.get("labels"):
            label_args = [x.strip() for x in args.get("labels").split(",")]
            query["$and"] = [{"labels": {"$in": [label]}} for label in label_args]
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
