from utils import mongo


class MpsApi:
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.api_mps
        self._remuneration = "influences.register_of_interests.remuneration_total"
        self._funding = "influences.electoral_commision.donation_total"
        self._remuneration_search = None
        self._funding_search = None
        self.query = None

    def request(self, args):
        return self._fetch(args)

    def _fetch(self, args):
        self.query = {}
        response_data = []
        page_size = 20
        skip_to = 0
        print "*args", args
        self._filter_party(args)
        self._filter_interests(args)
        self._filter_funding(args)
        if len(self.query) > 0:
            print self.query
            results = self.cache_data.find(self.query).skip(skip_to).limit(page_size)
        else:
            results = self.cache_data.find().skip(skip_to).limit(page_size)
        for entry in results:
            detail = {
                "name": entry["name"],
                "party": entry["party"],
                "image": entry["image_url"],
                "influences": entry["influences"],
                "positions": entry["government_positions"],
                "weight": entry["weight"]
            }
            response_data.append(detail)
        results = {"results": results.count()}
        return [results, response_data]

    def _filter_party(self, args):
        if args["party"]:
            self.query["party"] = args["party"]

    def _filter_interests(self, args):
        self._remuneration_search = {}
        if args["interests_gt"] and args["interests_lt"]:
            self._remuneration_search["$gt"] = args["interests_gt"]
            self._remuneration_search["$lt"] = args["interests_lt"]
            self.query[self._remuneration] = self._remuneration_search
        elif args["interests_gt"]:
            self._remuneration_search["$gt"] = args["interests_gt"]
            self.query[self._remuneration] = self._remuneration_search
        elif args["interests_lt"]:
            self._remuneration_search["$lt"] = args["interests_lt"]
            self.query[self._remuneration] = self._remuneration_search

    def _filter_funding(self, args):
        self._funding_search = {}
        if args["donations_gt"] and args["donations_lt"]:
            self._funding_search["$gt"] = args["donations_gt"]
            self._funding_search["$lt"] = args["donations_lt"]
            self.query[self._funding] = self._funding_search
        elif args["donations_gt"]:
            self._funding_search["$gt"] = args["donations_gt"]
            self.query[self._funding] = self._funding_search
        elif args["donations_lt"]:
            self._funding_search["$lt"] = args["donations_lt"]
            self.query[self._funding] = self._funding_search