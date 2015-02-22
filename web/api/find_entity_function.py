from web.api import BaseAPI
from utils import mongo
from data_models import core
from data_interfaces import search_interface


class EntityApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.api_lords
        self.data_model = core.BaseDataModel()
        self._elastic = search_interface.SearchInterface()

    def request(self, args):
        #return self._fetch(args)
        return self._search(args)

    def _fetch(self, args):
        search = args["search"]
        response_data = []
        print "searching mongo for:", search
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

    def _search(self, args):
        mps_endpoint = "api_mps"
        search_string = {
            "query": {
                "query_string": {
                "query": u"name:{}".format(args["search"])
                }
            }
        }
        print "elastic search for:", search_string
        return self._elastic.search(mps_endpoint, search_string)