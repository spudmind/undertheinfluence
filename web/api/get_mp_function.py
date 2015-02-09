from web.api import BaseAPI
from data_models import models
from utils import mongo


class MpApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.api_mps
        self.data_models = models

    def request(self, args):
        return self._fetch(args)

    def _fetch(self, args):
        api_query = {}
        response_data = {}
        name = args["name"]
        api_query["name"] = name
        api_entry = list(self.cache.db.api_mps.find(api_query))
        if len(api_entry) == 1:
            mp = self.data_models.MemberOfParliament(name)
            detail = {
                "register_of_interests": self._interest_urls(mp.interests),
                "electoral_commission": self._donor_urls(mp.donations)
            }
            response_data = {
                "name": api_entry[0]["name"],
                "party": api_entry[0]["party"],
                "twfy_id": api_entry[0]["twfy_id"],
                "image_url": api_entry[0]["image_url"],
                "government_positions": api_entry[0]["government_positions"],
                "influences_summary": api_entry[0]["influences"],
                "influences_detail": detail
            }
        return response_data

    def _interest_urls(self, interests):
        results = []
        for interest in interests:
            updated = interest
            interest_name = interest["interest"]["name"]
            interest_labels = interest["interest"]["labels"]
            urls = self.named_entity_resources(interest_name, interest_labels)
            updated["interest"]["details_url"] = urls[0]
            updated["interest"]["api_url"] = urls[1]
            results.append(updated)
        return results

    def _donor_urls(self, donations):
        results = []
        for donation in donations:
            updated = donation
            donor_name = donation["donor"]["name"]
            donor_labels = donation["donor"]["labels"]
            urls = self.named_entity_resources(donor_name, donor_labels)
            updated["donor"]["details_url"] = urls[0]
            updated["donor"]["api_url"] = urls[1]
            results.append(updated)
        return results

