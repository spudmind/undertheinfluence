from web.api import BaseAPI
from data_models import models
from utils import mongo


class LordApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_lords'

    def request(self, query):
        name = query["name"]
        result, _ = self._db.query(self._db_table, query=query)
        if len(result) > 0:
            fields = ["name", "party", "twfy_id", "influences"]
            rename_field = {"influences": "influences_summary"}
            result = {rename_field.get(k, k): v for k, v in result[0].items() if k in fields}
            lord = models.Lord(name)
            result['influences_detail'] = {
                "register_of_interests": self._interest_urls(lord.interests),
                "electoral_commission": self._recipient_urls(lord.donations),
            }
        return result

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

    def _recipient_urls(self, donations):
        results = []
        for donation in donations:
            updated = donation
            recipient_name = donation["recipient"]["name"]
            recipient_labels = donation["recipient"]["labels"]
            urls = self.named_entity_resources(recipient_name, recipient_labels)
            updated["recipient"]["details_url"] = urls[0]
            updated["recipient"]["api_url"] = urls[1]
            results.append(updated)
        return results
