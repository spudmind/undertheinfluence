from utils import mongo


class SummaryApi:
    def __init__(self):
        self._db = mongo.MongoInterface()
        self._db_table = 'api_political_parties'

    def request(self):
        results, response = self._db.query(self._db_table, query=query, page=page)

