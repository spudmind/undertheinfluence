from data_models.influencers_models import Influencer
from web.api import BaseAPI
from utils import mongo
from utils import config


class InfluencerApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self.lords_titles = config.lords_titles
        self._db_table = 'api_influencers'

    def request(self, args):
        name = args["name"]
        result, _ = self._db.query(self._db_table, query=args)
        if len(result) > 0:
            influencer = Influencer(name)
            register = self._nest_category(self._interest_urls(influencer.interests))
            ec = self._recipient_urls(influencer.donations)
            lobby = self._lobby_urls(influencer.lobbyists)
            meetings = self._politician_urls(influencer.meetings)
            result = {
                'name': result[0]['name'],
                'influences_summary': result[0]['influences'],
                'influences_detail': {
                    "lobby_registers": lobby,
                    "register_of_interests": register,
                    "electoral_commission": ec,
                    "meetings": meetings
                },
            }
        return result

    def _lobby_urls(self, lobbyists):
        results = []
        for lobby in lobbyists:
            updated = {
                "agency": {
                    "name": lobby["name"],
                    "details_url": self.named_entity_resources(
                        lobby["name"], "Lobby Agency"
                    )[0],
                    "contact_details": lobby["contact_details"]
                },
                "from": lobby["from"],
                "to": lobby["to"]
            }

            results.append(updated)
        return results

    def _interest_urls(self, interests):
        results = []
        for interest in interests:
            updated = interest
            interest_name = interest["interest"]["name"]
            interest_labels = interest["interest"]["labels"]
            urls = self.named_entity_resources(interest_name, interest_labels)
            updated["interest"]["details_url"] = urls[0]
            updated["interest"]["api_url"] = urls[1]
            results.append(updated)
        return results

    def _recipient_urls(self, donations):
        results = []
        for donation in donations:
            updated = donation
            recipient_name = donation["recipient"]["name"]
            recipient_labels = donation["recipient"]["labels"]
            urls = self.named_entity_resources(recipient_name, recipient_labels)
            updated["recipient"]["details_url"] = urls[0]
            updated["recipient"]["api_url"] = urls[1]
            results.append(updated)
        return results

    def _politician_urls(self, meetings):
        results = []
        for meeting in meetings:
            updated = meeting
            host_name = {"name": meeting["host"], "details_url": None}
            if meeting["host"]:
                if any(title in meeting["host"] for title in self.lords_titles):
                    label = "lord"
                else:
                    label = "mp"
                urls = self.named_entity_resources(meeting["host"], label)
                host_name["details_url"] = urls[0]
                updated["host"] = host_name
            results.append(updated)
        return results