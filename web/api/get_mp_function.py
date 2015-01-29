from data_models import models
from utils import mongo


class MpApi:
    def __init__(self):
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
                "register_of_interests": mp.interests,
                "electoral_commision": mp.donations
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



