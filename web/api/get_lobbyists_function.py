from web.api import BaseAPI
from flask import url_for
from utils import mongo


class LobbyistsApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_lobbyists'

    def request(self, **args):
        page = args.get('page', 1)
        query = {}
        results, response = self._db.query(self._db_table, query=query, page=page)
        if response['has_more']:
            next_query = args
            next_query['page'] = page + 1
            response['next_url'] = url_for('getLobbyAgencies', _external=True, **next_query)

        response["results"] = [
            {
                "name": entry["name"],
                "influences_summary": self._influencer_urls(entry["influences"]),
                "labels": entry["labels"],
                "detail_url": url_for(
                    'show_politicians', government_department=entry["name"], _external=True
                )
            }
            for entry in results
        ]
        return response

    def _influencer_urls(self, influences):
        results = []
        for entry in influences["lobbying_registers"]["clients"]:
            updated = {}
            updated["name"] = entry["name"]
            updated["details_url"]= self.named_entity_resources(
                entry["name"], entry["labels"]
            )[0]
            results.append(updated)
        influences["lobbying_registers"]["clients"] = results
        return influences