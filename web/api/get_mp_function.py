from web.api import BaseAPI
from data_models import government_models
from utils import mongo


class MpApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self._db_table = 'api_mps'

    def request(self, args):

        name = args['name']
        result, _ = self._db.query(self._db_table, query=args)

        if len(result) > 0:
            mp = government_models.MemberOfParliament(name)
            meetings = self._influencer_urls(mp.meetings)
            #interests = self._nest_category(self._interest_urls(mp.interests))
            interests = self._interest_urls(mp.interests)
            donations = self._donor_urls(mp.donations)
            result = {
                'name': result[0]['name'],
                'party': result[0]['party'],
                'influences_summary': result[0]['influences'],
                'influences_detail': {
                    "register_of_interests": interests,
                    "electoral_commission": donations,
                    "meetings": meetings
                },
                "government_departments": self._department_detail_urls(
                    result[0]["government_departments"]
                ),
                "government_positions": result[0]["government_positions"],
                "government_committees": self._committee_detail_urls(
                    result[0]["government_committees"]
                ),
                'mp': mp.mp_website,
                'wikipedia': mp.wikipedia,
                'guardian': mp.guardian,
                'bbc': mp.bbc,
            }
        return result

    def _interest_urls(self, interests):
        results = []
        for category in interests:
            updated_interests = []
            for interest in category["interests"]:
                updated = interest
                interest_name = interest["interest"]["name"]
                interest_labels = interest["interest"]["labels"]
                urls = self.named_entity_resources(interest_name, interest_labels)
                updated["interest"]["details_url"] = urls[0]
                updated["interest"]["api_url"] = urls[1]
                updated_interests.append(updated)

            if len(updated_interests) > 0:
                category["interests"] = updated_interests
                results.append(category)

        return results

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