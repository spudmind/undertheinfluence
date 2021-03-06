from web.api import BaseAPI
from flask import url_for
from utils import mongo


class CommitteesApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_committees'

    def request(self, **args):
        page = args.get('page', 1)
        query = {}
        results, response = self._db.query(self._db_table, query=query, page=page)
        if response['has_more']:
            next_query = args
            next_query['page'] = page + 1
            response['next_url'] = url_for('getCommittees', _external=True, **next_query)

        response["results"] = [
            {
                "name": entry["name"],
                "influences_summary": entry["influences"],
                "labels": entry["labels"],
                "members": self._members_detail_url(
                    entry["members"]
                ),
                "mp_count": entry["mp_count"],
                "detail_url": url_for(
                    'show_politicians_detail', government_committee=entry["name"], _external=True
                )
            }
            for entry in results
        ]
        return response

