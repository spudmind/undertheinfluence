from utils import mongo
from flask import url_for


class PoliticalPartiesApi:
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.api_political_parties
        self.query = None

    def request(self, **args):
        return self._fetch(args)

    def _fetch(self, args):
        self.query = {}
        response_data = []
        page_size = 20
        skip_to = 0
        print "*args", args
        if len(self.query) > 0:
            results = self.cache_data.find(self.query).skip(skip_to).limit(page_size)
        else:
            results = self.cache_data.find().skip(skip_to).limit(page_size)
        for entry in results:
            detail_url = url_for('show_party', name=entry["name"], _external=True)
            detail = {
                "name": entry["name"],
                "image_url": "None",
                "influences_summary": entry["influences"],
                "weight": entry["weight"],
                "mp_count": entry["mp_count"],
                "lord_count": entry["lord_count"],
                "detail_url": detail_url
            }
            response_data.append(detail)
        results = {"results": results.count()}
        return [results, response_data]