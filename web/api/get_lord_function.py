from data_models import models
from utils import mongo


class LordApi:
    def __init__(self):
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
                "register_of_interests": lord.interests,
                "electoral_commission": lord.donations
            }
        return result



