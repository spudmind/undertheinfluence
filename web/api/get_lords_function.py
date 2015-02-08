from utils import mongo
from flask import url_for

class LordsApi:
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.api_lords
        self._funding = "influences.electoral_commission.donation_total"
        self._funding_search = None
        self.query = None

    def request(self, **args):
        return self._fetch(args)

    def _fetch(self, args):
        self.query = {}
        response_data = []
        page_size = 20
        skip_to = 0
        print "*args", args
        self._filter_party(args)
        self._filter_funding(args)
        if len(self.query) > 0:
            print self.query
            results = self.cache_data.find(self.query).skip(skip_to).limit(page_size)
        else:
            results = self.cache_data.find().skip(skip_to).limit(page_size)
        for entry in results:
            detail_url = url_for('show_lord', name=entry["name"], _external=True)

            detail = {
                "name": entry["name"],
                "party": entry["party"],
                "image_url": None,
                "detail_url": detail_url,
                "weight": entry["weight"],
                "twfy_id": entry["twfy_id"],
                "influences_summary": entry["influences"]
            }
            response_data.append(detail)
        # return {
        #     "total": results.count(),
        #     "results": response_data,
        # }
        return response_data

    def _filter_party(self, args):
        if args.get("party"):
            self.query["party"] = args.get("party")

    def _filter_funding(self, args):
        _funding_search = {}
        if args.get("donations_gt") and args.get("donations_lt"):
            _funding_search["$gt"] = args.get("donations_gt")
            _funding_search["$lt"] = args.get("donations_lt")
            self.query[self._funding] = _funding_search
        elif args.get("donations_gt"):
            _funding_search["$gt"] = args.get("donations_gt")
            self.query[self._funding] = _funding_search
        elif args.get("donations_lt"):
            _funding_search["$lt"] = args.get("donations_lt")
            self.query[self._funding] = _funding_search