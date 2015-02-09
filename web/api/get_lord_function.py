from data_models import models
from utils import mongo


class LordApi:
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.api_lords
        self.data_models = models

    def request(self, args):
        return self._fetch(args)

    def _fetch(self, args):
        api_query = {}
        response_data = {}
        name = args["name"]
        api_query["name"] = name
        api_entry = list(self.cache.db.api_lords.find(api_query))
        if len(api_entry) == 1:
            lord = self.data_models.Lord(name)
            detail = {
                "register_of_interests": lord.interests,
                "electoral_commission": lord.donations
            }
            response_data = {
                "name": api_entry[0]["name"],
                "party": api_entry[0]["party"],
                "twfy_id": api_entry[0]["twfy_id"],
                "influences_summary": api_entry[0]["influences"],
                "influences_detail": detail
            }
        return response_data



