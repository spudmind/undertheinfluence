from utils import mongo


class MpsApi:
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.api_lords
        self._funding = "influences.electoral_commission.donation_total"
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
        self._filter_funding(args)
        if len(self.query) > 0:
            print self.query
            results = self.cache_data.find(self.query).skip(skip_to).limit(page_size)
        else:
            results = self.cache_data.find().skip(skip_to).limit(page_size)
        for entry in results:
            register = entry["influences"]["register_of_interests"]
            ec = entry["influences"]["electoral_commission"]
            detail = {
                "name": entry["name"],
                "party": entry["party"],
                "register_of_interests_categories": register["interest_categories"],
                "register_of_interests_relationships": register["interest_relationships"],
                "electoral_commission_total": ec["donation_total"],
                "electoral_commission_count": ec["donation_count"],
                "weight": entry["weight"]
            }
            response_data.append(detail)
        # return {
        #     "total": results.count(),
        #     "results": response_data,
        # }
        return response_data

    def _filter_party(self, args):
        if args["party"]:
            self.query["party"] = args["party"]

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