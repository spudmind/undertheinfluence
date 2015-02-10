from data_models import models
from utils import mongo


class InfluencerApi:
    def __init__(self):
        self._db = mongo.MongoInterface()
        self._db_table = 'api_influencers'

    def request(self, query):
        name = query["name"]
        result, _ = self._db.query(self._db_table, query=query)
        if len(result) > 0:
            influencer = models.Influencer(name)
            result = {
                'name': result[0]['name'],
                'influences_summary': result[0]['influences'],
                'influences_detail': {
                    "register_of_interests": influencer.interests,
                    "electoral_commission": influencer.donations
                },
            }
        return result
