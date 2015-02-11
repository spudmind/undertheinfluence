from web.api import BaseAPI
from data_models import models
from utils import mongo


class PoliticalPartyApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.api_political_parties
        self.data_models = models

    def request(self, args):
        return self._fetch(args)

    def _fetch(self, args):
        api_query = {}
        response_data = {}
        name = args["name"]
        api_query["name"] = name
        api_entry = list(self.cache_data.find(api_query))
        if len(api_entry) == 1:
            party = self.data_models.PoliticalParty(name)
            detail = {
                "electoral_commission": self._donor_urls(party.donations)
            }
            response_data = {
                "name": api_entry[0]["name"],
                "image_url": None,
                "influences_summary": api_entry[0]["influences"],
                "influences_detail": detail
            }
        return response_data

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

