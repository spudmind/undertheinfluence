from data_models.influencers import Influencer
from web.api import BaseAPI
from data_models import government
from utils import mongo


class InfluencerApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_influencers'

    def request(self, args):
        name = args["name"]
        result, _ = self._db.query(self._db_table, query=args)
        if len(result) > 0:
            influencer = Influencer(name)
            result = {
                'name': result[0]['name'],
                'influences_summary': result[0]['influences'],
                'influences_detail': {
                    "register_of_interests": self._nest_category(
                        self._interest_urls(influencer.interests)
                    ),
                    "electoral_commission": self._recipient_urls(influencer.donations),
                },
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
