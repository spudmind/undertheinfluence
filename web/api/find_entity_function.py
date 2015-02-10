from web.api import BaseAPI
from utils import mongo
from data_models import core


class EntityApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.api_lords
        self.data_model = core.BaseDataModel()

    def request(self, **args):
        return self._fetch(args)

    def _fetch(self, args):
        search = args["search"]
        response_data = []
        search_results = self.data_model.find_entity(search)
        for entry in search_results:
            labels = entry["labels"]
            name = entry["name"]
            web_url, api_url = self.named_entity_resources(name, labels)
            detail = {
                "name": name,
                "labels": labels,
                "details_url": web_url,
                "api_url": api_url
            }
            response_data.append(detail)
        return response_data