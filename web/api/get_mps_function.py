from utils import mongo


class MpsApi:
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.api_mps
        self._remuneration = "influences.register_of_interests.remuneration_total"
        self._funding = "influences.electoral_commision.donation_total"
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
        self._filter_interests(args)
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
                "image": entry["image_url"],
                "register_of_interests_categories": register["interest_categories"],
                "register_of_interests_relationships": register["interest_relationships"],
                "register_of_interests_count": register["remuneration_count"],
                "register_of_interests_total": register["remuneration_total"],
                "electoral_commission_total": ec["donation_total"],
                "electoral_commission_count": ec["donor_count"],
                "positions": entry["government_positions"],
                "weight": entry["weight"]
            }
            response_data.append(detail)
        # return {
        #     "total": results.count(),
        #     "results": response_data,
        # }
        return response_data

    def _filter_party(self, args):
        if args.get("party") is not None:
            self.query["party"] = args.get("party")

    def _filter_interests(self, args):
        _remuneration_search = {}
        if args.get("interests_gt"):
            _remuneration_search["$gt"] = args.get("interests_gt")
        elif args.get("interests_lt"):
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
