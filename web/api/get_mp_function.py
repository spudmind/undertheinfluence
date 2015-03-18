from web.api import BaseAPI
from data_models import government_models
from utils import mongo


class MpApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_mps'

    def request(self, args):
        name = args['name']
        result, _ = self._db.query(self._db_table, query=args)

        if len(result) > 0:
            mp = government_models.MemberOfParliament(name)
            result = {
                'name': result[0]['name'],
                'party': result[0]['party'],
                'influences_summary': result[0]['influences'],
                'influences_detail': {
                    "register_of_interests": self._nest_category(
                        self._interest_urls(mp.interests)
                    ),
                    "electoral_commission": self._donor_urls(mp.donations),
                },
                "government_positions": result[0]["government_positions"],
                "government_departments": self._department_detail_urls(
                    result[0]["government_departments"]
                ),
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

    def _donor_urls(self, donations):
        results = []
        for donation in donations:
            updated = donation
            donor_name = donation["donor"]["name"]
            donor_labels = donation["donor"]["labels"]
            urls = self.named_entity_resources(donor_name, donor_labels)
            updated["donor"]["details_url"] = urls[0]
            updated["donor"]["api_url"] = urls[1]
            results.append(updated)
        return results
