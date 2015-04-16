from web.api import BaseAPI
from data_models import government_models
from utils import mongo


class LordApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_lords'

    def request(self, args):
        name = args["name"]
        result, _ = self._db.query(self._db_table, query=args)
        if len(result) > 0:
            lord = government_models.Lord(name)
            result = {
                'name': result[0]['name'],
                'influences_summary': result[0]['influences'],
                'influences_detail': {
                    "register_of_interests": self._interest_urls(lord.interests),
                    "electoral_commission": self._recipient_urls(lord.donations),
                },
            }
        return result

    def _interest_urls(self, interests):
        results = []
        for entry in interests:
            updated_interests = []
            for interest in entry["interests"]:
                updated = interest
                interest_name = interest["interest"]["name"]
                interest_labels = interest["interest"]["labels"]
                urls = self.named_entity_resources(interest_name, interest_labels)
                updated["interest"]["details_url"] = urls[0]
                updated["interest"]["api_url"] = urls[1]
                updated_interests.append(updated)

            if len(updated_interests) > 1:
                entry["interests"] = updated_interests
                results.append(entry)
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

