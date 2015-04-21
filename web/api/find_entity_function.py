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
        field = 'name'
        query = args["search"]
        results, response = self._elastic.search(field, query)

        for entry in results:
            print entry
            print entry["labels"]

        response["results"] = [
            {
                "name": entry["name"],
                "party": self._fill_missing("party", entry),
                "image_url": self._fill_missing("image_url", entry),
                "detail_url": self.named_entity_resources(
                    entry["name"], entry["labels"]
                )[0],
                "weight": self._get_weight(entry),
                "members": self._members_detail_url(
                    self._get_members(entry)
                ),
                "labels": entry["labels"],
                "influences_summary": entry["influences"]
            }
            for entry in results
        ]
        return response
