from data_models import models
from utils import mongo


class InfluencerApi:
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.api_influencers
        self.data_models = models

    def request(self, args):
        return self._fetch(args)

    def _fetch(self, args):
        api_query = {}
        response_data = {}
        name = args["name"]
        api_query["name"] = name
        party = None
        api_entry = list(self.cache.db.api_influencers.find(api_query))
        if len(api_entry) == 1:
            influencer = self.data_models.Influencer(name)
            detail = {
                "register_of_interests": influencer.interests,
                "electoral_commission": influencer.donations
            }
            response_data = {
                "name": api_entry[0]["name"],
                "influences_summary": api_entry[0]["influences"],
                "influences_detail": detail
            }
        return response_data



