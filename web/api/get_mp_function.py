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
        response_data = []
        name = args["name"]