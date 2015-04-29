from web.api import BaseAPI
from utils import mongo
from utils import config
from flask import url_for


class InfluencersApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_influencers'
        self.lords_titles = config.lords_titles
        self._remuneration = "influences.register_of_interests.remuneration_total_int"
        self._funding = "influences.electoral_commission.donation_total_int"
        self._lobbyists = "influences.lobby_registers.lobbyist_hired"
        #TODO update this search to use meetings_count once updated in api_gen
        self._meetings = "influences.meetings.meeting_count"
        self.query = {}

    def request(self, **args):
        pager = {}
        page = args.get('page', 1)

        self._filter_labels(args)
        self._filter_meetings(args)
        self._filter_interests(args)
        self._filter_funding(args)
        self._filter_lobbyists(args)

        results, response = self._db.query(self._db_table, query=self.query, page=page)

        if response['has_more']:
            next_query = args
            next_query['page'] = page + 1
            response['next_url'] = url_for('getInfluencers', _external=True, **next_query)
            pager["next"] = url_for('show_influencers_detail', _external=True, **next_query)
        if page > 1:
            previous_query = args
            previous_query['page'] = page - 1
            pager["previous"] = url_for('show_influencers_detail', _external=True, **previous_query)

        response['pager'] = pager

        response["results"] = [{
            "name": entry["name"],
            "image_url": None,
            "influences_summary": self._politician_urls(entry["influences"]),
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

    def _filter_meetings(self, args):
        _meetings_search = {}
        if args.get("meetings_gt"):
            _meetings_search["$gt"] = int(args.get("meetings_gt"))
        if args.get("meetings_lt"):
            _meetings_search["$lt"] = int(args.get("meetings_lt"))
        if _meetings_search != {}:
            self.query[self._meetings] = _meetings_search

    def _filter_interests(self, args):
        _remuneration_search = {}
        if args.get("interests_gt"):
            _remuneration_search["$gt"] = int(args.get("interests_gt"))
        if args.get("interests_lt"):
            _remuneration_search["$lt"] = int(args.get("interests_lt"))
        if _remuneration_search != {}:
            self.query[self._remuneration] = _remuneration_search

    def _filter_funding(self, args):
        _funding_search = {}
        if args.get("donations_gt"):
            _funding_search["$gt"] = int(args.get("donations_gt"))
        if args.get("donations_lt"):
            _funding_search["$lt"] = int(args.get("donations_lt"))
        if _funding_search != {}:
            self.query[self._funding] = _funding_search

    def _filter_lobbyists(self, args):
        _lobby_search = {}
        if args.get("lobbyists_gt"):
            _lobby_search["$gt"] = int(args.get("lobbyists_gt"))
        if args.get("lobbyists_lt"):
            _lobby_search["$lt"] = int(args.get("lobbyists_lt"))
        if _lobby_search != {}:
            self.query[self._lobbyists] = _lobby_search

    def _politician_urls(self, influences):
        results = []
        if "meetings" in influences:
            for entry in influences["meetings"]["politicians_met"]:
                updated = {}
                if any(title in entry for title in self.lords_titles):
                    label = "lord"
                else:
                    label = "mp"
                updated["name"] = entry
                updated["details_url"] = self.named_entity_resources(
                    entry, label
                )[0]
                #print "updated", updated
                results.append(updated)
            influences["meetings"]["politicians_met"] = results
        return influences