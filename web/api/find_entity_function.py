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
        merged_results = self._merge_duplicates(results)

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
            for entry in merged_results
        ]
        return response

    @staticmethod
    def _merge_duplicates(search_results):
        merged_results = {}
        seen = set()
        seen_add = seen.add
        result_order = [
            y for y in [x["name"] for x in search_results]
            if not (y in seen or seen_add(y))
        ]
        for entry in search_results:
            name = entry["name"]
            if name not in merged_results:
                merged_results[name] = entry
            else:
                existing_influences = merged_results[name]["influences"]
                extra_influences = entry["influences"]

                merged_influences = dict(existing_influences)
                merged_influences.update(extra_influences)

                merged_results[name].update(entry)
                merged_results[name]["influences"] = merged_influences

        return [merged_results[entry] for entry in result_order]
