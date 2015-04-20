from web.api import BaseAPI
from data_models import influencers_models
from utils import mongo


class LobbyAgencyApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_lobbyists'

    def request(self, args):
        name = args['name']
        result, _ = self._db.query(self._db_table, query=args)

        if len(result) > 0:
            result = {
                "name": result[0]["name"],
                "influences_summary": self._influencer_urls(result[0]["influences"]),
                "labels": result[0]["labels"],
                "contact_details": result[0]["contact_details"].replace("\n", "<br />"),
            }
        return result

    def _influencer_urls(self, influences):
        results = []
        for entry in influences["lobbying_registers"]["clients"]:
            updated = entry
            updated["details_url"] = self.named_entity_resources(
                entry["name"], entry["labels"]
            )[0]
            results.append(updated)
        influences["lobbying_registers"]["clients"] = results
        return influences