from data_models import government_models
from web.api import BaseAPI
from flask import url_for
from utils import mongo


class OfficesApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_government'

    def request(self, **args):
        page = args.get('page', 1)

        all_offices = government_models.GovernmentOffices().get_all()
        result = []
        for dept, labels, weight in all_offices:
            office = government_models.GovernmentOffice(dept)
            entry = {
                "name": dept,
                "labels": labels,
                "weight": weight,
                "influences": {
                    "register_of_interests": office.interests_summary,
                    "electoral_commission": office.donation_summary
                }
            }
            result.append(entry)
        return result

