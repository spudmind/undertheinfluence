from web.api import BaseAPI
from utils import mongo
import json


class DataApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self.query = {}
        self.fields = {
            "donation_count": "$influences.electoral_commission.donation_count",
            "donor_count": '$influences.electoral_commission.donor_count',
            "donation_total_int": "$influences.electoral_commission.donation_total_int",
            "mp_interest_relationships": "$influences.register_of_interests.relationship_count",
            "lord_interest_relationships": "$influences.register_of_interests.interest_relationships",
            "remuneration_count": "$influences.register_of_interests.remuneration_count",
            "remuneration_total_int": "$influences.register_of_interests.remuneration_total_int",
            "lobbyists_hired": "$influences.lobby_registers.lobbyist_hired"
        }

    def request(self, **args):
        node_type = args.get("type")
        category = args.get("category")
        field = args.get("field")
        summary = {
            "influencers": self._influencers_aggregate(category, field),
            #"lobby_agencies": self._influencers_aggregate(),
            "political_parties": self._party_aggregate(category, field),
            "mps": self._mp_aggregate(category, field),
            "lords": self._lord_aggregate(category, field)
        }

        return {"children": summary[node_type][category]}

    def _influencers_aggregate(self, category, field):
        _db_table = 'api_influencers'
        response = {}

        if category == "electoral_commission":
            # get electoral commission data
            ec_fields = ["donation_total_int", "donation_count"]
            top_total, top_count = self._get_top(_db_table, ec_fields)
            ec = {
                "donation_total": self._format_top(top_total, "influencer"),
                "donation_count": self._format_top(top_count, "influencer", monetary=False)
            }
            response["electoral_commission"] = ec[field]

        if category == "register_of_interests":
            # get register of interests data
            reg_fields = [
                "remuneration_total_int",
                "mp_interest_relationships",
                "remuneration_count"
            ]
            top_total, top_relationships, top_count = self._get_top(_db_table, reg_fields)
            reg = {
                "remuneration_total": self._format_top(top_total, "influencer"),
                "interest_relationships": self._format_top(
                    top_relationships, "influencer", monetary=False
                ),
                "remuneration_count": self._format_top(
                    top_count, "influencer", monetary=False
                )
            }
            response["register_of_interests"] = reg[field]
        return response

    def _party_aggregate(self, category, field):
        _db_table = 'api_political_parties'
        response = {}
        if category == "political_parties":
            ec_fields = ["donation_total_int", "donation_count"]
            top_total, top_count = self._get_top(_db_table, ec_fields)
            result = {
                "donation_total": self._format_top(top_total, "party"),
                "donation_count": self._format_top(top_count, "party", monetary=False)
            }
            response["electoral_commission"] = result[field]
        return response

    def _mp_aggregate(self, category, field):
        _db_table = 'api_mps'
        response = {}

        if category == "electoral_commission":
            # get electoral commission data
            ec_fields = ["donation_total_int", "donor_count"]
            top_total, top_count = self._get_top(_db_table, ec_fields)
            ec = {
                "donation_total": self._format_top(top_total, "mp"),
                "donor_count": self._format_top(top_count, "mp", monetary=False)
            }
            response["electoral_commission"] = ec[field]

        if category == "register_of_interests":
            # get register of interests data
            reg_fields = [
                "remuneration_total_int",
                "lord_interest_relationships",
                "remuneration_count"
            ]
            top_total, top_relationships, top_count = self._get_top(_db_table, reg_fields)
            reg = {
                "remuneration_total": self._format_top(top_total, "mp"),
                "interest_relationships": self._format_top(
                    top_relationships, "mp", monetary=False
                ),
                "remuneration_count": self._format_top(
                    top_count, "mp", monetary=False
                )
            }
            response["register_of_interests"] = reg[field]
        return response

    def _lord_aggregate(self, category, field):
        _db_table = 'api_lords'
        response ={}

        if category == "electoral_commission":
            # get electoral commission data
            ec_fields = ["donation_total_int", "donation_count"]
            top_total, top_count = self._get_top(_db_table, ec_fields)
            ec = {
                "donation_total": self._format_top(top_total, "lord"),
                "donation_count": self._format_top(top_count, "lord", monetary=False)
            }
            response["electoral_commission"] = ec[field]

        if category == "register_of_interests":
            # get register of interests data
            reg_fields = ["lord_interest_relationships"]
            top_relationships = self._get_top(_db_table, reg_fields)[0]
            reg = {
                "interest_relationships": self._format_top(
                    top_relationships, "lord", monetary=False
                )
            }
            response["register_of_interests"] = reg[field]
        return response

    def _format_top(self, results, label, monetary=True):
        updated = []
        for entry in results:
            new = {
                "name": entry["_id"],
                "details_url": self.named_entity_resources(
                    entry["_id"], label
                )[0]
            }
            if monetary:
                new["total_int"] = entry["total"]
                new["total"] = self._format_number(entry["total"])
            else:
                new["total"] = entry["total"]
            updated.append(new)
        return updated

    def _get_aggregate(self, table, field_list):
        return [self._db.sum(table, field=self.fields[x]) for x in field_list]

    def _get_top(self, table, field_list):
        return [self._db.top(table, field=self.fields[x]) for x in field_list]
