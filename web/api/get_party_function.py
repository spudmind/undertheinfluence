from web.api import BaseAPI
from data_models import government_models
from utils import mongo


class PoliticalPartyApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_political_parties'

    def request(self, args):
        return self._fetch(args)

    def _fetch(self, args):
        response_data = {}
        name = args["name"]
        page = args.get('page', 1)

        query = {"name": name}
        result, _ = self._db.query(self._db_table, query=query, page=page)

        if len(result) > 0:
            party = government_models.PoliticalParty(name)
            detail = {
                "electoral_commission": self._donor_urls(party.donations)
            }
            response_data = {
                "name": result[0]["name"],
                "image_url": None,
                "influences_summary": result[0]["influences"],
                "influences_detail": detail
            }
        return response_data

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

