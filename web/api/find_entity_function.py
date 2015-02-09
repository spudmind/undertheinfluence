from utils import mongo
from data_models import core
from flask import url_for


class EntityApi:
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.api_lords
        self.data_model = core.BaseDataModel()

    def request(self, **args):
        return self._fetch(args)

    def _fetch(self, args):
        search = args["search"]
        response_data = []
        search_results = self.data_model.find_entity(search)
        for entry in search_results:
            labels = entry["labels"]
            name = entry["name"]
            if "Member of Parliament" in labels:
                api_details_url = u"/api/v0.1/getMp?name={0}".format(name)
                details_url = url_for('show_mp', name=name, _external=True)
                detail = {
                    "name": name,
                    "labels": labels,
                    "details_url": details_url,
                    "api_details_url": api_details_url
                }
                response_data.append(detail)
            elif "Lord" in labels:
                api_details_url = u"/api/v0.1/getLord?name={0}".format(name)
                details_url = url_for(
                    'show_lord', name=entry["name"], _external=True
                )
                detail = {
                    "name": entry["name"],
                    "labels": labels,
                    "details_url": details_url,
                    "api_details_url": api_details_url
                }
                response_data.append(detail)
            elif "Donor" in labels or "Registered Interest" in labels:
                api_details_url = u"/api/v0.1/getInfluencer?name={0}".format(name)
                details_url = url_for(
                    'show_influencer', name=entry["name"], _external=True
                )
                detail = {
                    "name": entry["name"],
                    "labels": labels,
                    "details_url": details_url,
                    "api_details_url": api_details_url
                }
                response_data.append(detail)
        return response_data