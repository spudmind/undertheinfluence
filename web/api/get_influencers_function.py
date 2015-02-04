from utils import mongo


class InfluencersApi:
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.api_influencers
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
        self._filter_labels(args)
        self._filter_interests(args)
        self._filter_funding(args)
        if len(self.query) > 0:
            print "query",  self.query
            results = self.cache_data.find(self.query).skip(skip_to).limit(page_size)
        else:
            results = self.cache_data.find().skip(skip_to).limit(page_size)
        for entry in results:
            detail = {
                "name": entry["name"],
                "image": "None",
                "influences": entry["influences"],
                "labels": entry["labels"],
                "weight": entry["weight"]
            }
            response_data.append(detail)
        results = {"results": results.count()}
        return [results, response_data]

    def _filter_labels(self, args):
        if args["labels"]:
            label_args = [x.strip() for x in args["labels"].split(",")]
            label_query = []
            for label in label_args:
                label_query.append({"labels": {"$in": [label]}})
            self.query["$and"] = label_query

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