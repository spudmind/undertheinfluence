from utils import mongo
from flask import url_for


class PoliticalPartiesApi:
    def __init__(self):
        self._db = mongo.MongoInterface()
        self._db_table = 'api_political_parties'

    def request(self, **args):
        return self._fetch(args)

    def _fetch(self, args):
        page = args.get('page', 1)
        query = {}
        results, response = self._db.query(self._db_table, query=query, page=page)
        if response['has_more']:
            next_query = args
            next_query['page'] = page + 1
            response['next_url'] = url_for('getMps', _external=True, **next_query)

        response["results"] = [
            {
                "name": entry["name"],
                "image_url": entry["image_url"],
                "influences_summary": entry["influences"],
                "weight": entry["weight"],
                "mp_count": entry["mp_count"],
                "lord_count": entry["lord_count"],
                "detail_url": url_for(
                    'show_party', name=entry["name"], _external=True
                )
            }
            for entry in results
        ]
        return response
