from web.api import BaseAPI
from flask import url_for
from utils import mongo
from utils import config


class DepartmentsApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_departments'
        self.lords_titles = config.lords_titles

    def request(self, **args):
        page = args.get('page', 1)
        query = {}
        results, response = self._db.query(self._db_table, query=query, page=page)

        if response['has_more']:
            next_query = args
            next_query['page'] = page + 1
            response['next_url'] = url_for('getDepartments', _external=True, **next_query)

        response["results"] = [
            {
                "name": entry["name"],
                "influences_summary": self._politician_urls(entry["influences"]),
                "labels": entry["labels"],
                "members": self._members_detail_url(
                    entry["members"]
                ),
                "mp_count": entry["mp_count"],
                "detail_url": url_for(
                    'show_politicians_detail', government_department=entry["name"], _external=True

                )
            }
            for entry in results
        ]
        return response

    def _politician_urls(self, influences):
        results = []
        if "meetings_summary" in influences:
            for entry in influences["meetings_summary"]:
                updated = {}
                if any(title in entry["host"] for title in self.lords_titles):
                    label = "lord"
                else:
                    label = "mp"
                host = {
                    "name": entry["host"],
                    "details_url": self.named_entity_resources(
                        entry["host"], label
                    )[0]
                }
                updated["host"] = host
                updated["position"] = entry["position"]
                updated["meetings"] = entry["meetings"]
                #print "updated", updated
                results.append(updated)
            influences["meetings_summary"] = results
        return influences
