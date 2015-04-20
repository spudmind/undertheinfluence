from web.api import BaseAPI
from data_models import government_models
from utils import mongo


class LordApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_lords'

    def request(self, args):
        name = args["name"]
        result, _ = self._db.query(self._db_table, query=args)
        if len(result) > 0:
            lord = government_models.Lord(name)
            result = {
                'name': result[0]['name'],
                'influences_summary': result[0]['influences'],
                'influences_detail': {
                    "meetings": self._influencer_urls(lord.meetings),
                    "register_of_interests": self._interest_urls(lord.interests),
                    "electoral_commission": self._recipient_urls(lord.donations),
                },
                "government_departments": self._department_detail_urls(
                    result[0]["government_departments"]
                ),
                "government_positions": result[0]["government_positions"],
            }
        return result

    def _interest_urls(self, interests):
        results = []
        for entry in interests:
            updated_interests = []
            for interest in entry["interests"]:
                updated = interest
                interest_name = interest["interest"]["name"]
                interest_labels = interest["interest"]["labels"]
                urls = self.named_entity_resources(interest_name, interest_labels)
                updated["interest"]["details_url"] = urls[0]
                updated["interest"]["api_url"] = urls[1]
                updated_interests.append(updated)

            if len(updated_interests) > 1:
                entry["interests"] = updated_interests
                results.append(entry)
        return results

    def _recipient_urls(self, donations):
        results = []
        for donation in donations:
            print
            updated = donation
            recipient_name = donation["recipient"]["name"]
            recipient_labels = donation["recipient"]["labels"]
            urls = self.named_entity_resources(recipient_name, recipient_labels)
            updated["recipient"]["details_url"] = urls[0]
            updated["recipient"]["api_url"] = urls[1]
            results.append(updated)
        return results

    def _influencer_urls(self, meetings):
        results = []
        for meeting in meetings:
            updated = meeting
            attendee_name = {"name": meeting["attendee"], "details_url": None}
            if meeting["attendee"]:
                urls = self.named_entity_resources(meeting["attendee"], "influencer")
                attendee_name["details_url"] = urls[0]
                updated["attendee"] = attendee_name
            results.append(updated)
        return results
