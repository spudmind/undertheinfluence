from web.api import BaseAPI
from utils import mongo
from flask import url_for


class InfluencersApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_influencers'

        self._remuneration = "influences.register_of_interests.remuneration_total_int"
        self._funding = "influences.electoral_commission.donation_total_int"
        self._lobbyists = "influences.lobby_registers.lobbyist_hired"
        self.query = {}

    def request(self, **args):
        page = args.get('page', 1)

        self._filter_labels(args)
        self._filter_interests(args)
        self._filter_funding(args)
        self._filter_lobbyists(args)

        print "query:", self.query

        results, response = self._db.query(self._db_table, query=self.query, page=page)
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

    def _filter_labels(self, args):
        if args.get("labels"):
            label_args = [x.strip() for x in args.get("labels").split(",")]
            self.query["$and"] = [{"labels": {"$in": [label]}} for label in label_args]

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

    def _filter_lobbyists(self, args):
        _lobby_search = {}
        print args.get("lobbyists_gt")
        if args.get("lobbyists_gt"):
            _lobby_search["$gt"] = args.get("lobbyists_gt")
        if args.get("lobbyists_lt"):
            _lobby_search["$lt"] = args.get("lobbyists_lt")
        if _lobby_search != {}:
            self.query[self._lobbyists] = _lobby_search