from web.api import BaseAPI
from utils import mongo
from flask import url_for


class SummaryApi(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        self._db = mongo.MongoInterface()
        self.fields = {
            "donation_count": "$influences.electoral_commission.donation_count",
            "donor_count": '$influences.electoral_commission.donor_count',
            "donation_total_int": "$influences.electoral_commission.donation_total_int",
            "mp_interest_relationships": "$influences.register_of_interests.relationship_count",
            "lord_interest_relationships": "$influences.register_of_interests.interest_relationships",
            "remuneration_count": "$influences.register_of_interests.remuneration_count",
            "remuneration_total_int": "$influences.register_of_interests.remuneration_total_int",
            "lobbyists_hired": "$influences.lobby_registers.lobbyist_hired",
            "meetings_total": "$influences.meetings.meetings_total",
            "meetings_influencers": "$influences.meetings.meeting_count",
            "politician_count": "$influences.meetings.politician_count",
            "department_count": "$influences.meetings.department_count"
        }

    def request(self):
        apis = {
            "influencers": url_for('getInfluencers', _external=True),
            "lobby_agencies": url_for('getLobbyAgencies', _external=True),
            "political_parties": url_for('getPoliticalParties', _external=True),
            "politicians": url_for('getPoliticians', _external=True),
            "government_committees": url_for('getGovernmentCommittees', _external=True),
            "find_entity": url_for('findEntity', _external=True),
        }
        summary = {
            "influencers": self._influencers_aggregate(),
            #"lobby_agencies": self._influencers_aggregate(),
            "political_parties": self._party_aggregate(),
            "mps": self._mp_aggregate(),
            "lords": self._lord_aggregate()
        }

        content = {"summary": summary, "api_detail": apis}
        response = {
            "has_more": False,
            "page": 1,
            "per_page": 20,
            "results": content
        }
        return response

    def _influencers_aggregate(self):
        _db_table = 'api_influencers'
        meetings, result, ec, reg, lobby = {}, {}, {}, {}, {}

        result["count"] = self._format_number(self._db.count(_db_table), currency=False)

        # get meetings data
        meetings_fields = ["meetings_influencers", "politician_count", "department_count"]
        aggregates = self._get_aggregate(_db_table, meetings_fields)
        aggregate_total = aggregates[0]
        politician_total = aggregates[1]
        department_total = aggregates[2]
        meetings["meetings_total"] = self._format_number(aggregate_total, currency=False)
        meetings["politician_count"] = self._format_number(politician_total, currency=False)
        meetings["department_count"] = self._format_number(department_total, currency=False)
        top_total, pol_total, dept_total = self._get_top(_db_table, meetings_fields)
        meetings["top"] = {
            "meetings_total": self._format_top(top_total, "influencer", monetary=False),
            "politician_count": self._format_top(pol_total, "influencer", monetary=False),
            "department_count": self._format_top(dept_total, "influencer", monetary=False)
        }

        # get electoral commission data
        ec_fields = ["donation_total_int", "donation_count"]
        aggregates = self._get_aggregate(_db_table, ec_fields)
        aggregate_total = aggregates[0]
        aggregate_count = aggregates[1]

        ec["donation_total_int"] = aggregate_total
        ec["donation_total"] = self._format_number(aggregate_total)
        ec["donation_count"] = self._format_number(aggregate_count, currency=False)

        top_total, top_count = self._get_top(_db_table, ec_fields)
        ec["top"] = {
            "donation_total": self._format_top(top_total, "influencer"),
            "donation_count": self._format_top(top_count, "influencer", monetary=False)
        }

        # get register of interests data
        reg_fields = [
            "remuneration_total_int",
            "mp_interest_relationships",
            "remuneration_count"
        ]
        aggregates = self._get_aggregate(_db_table, reg_fields)
        aggregate_total = aggregates[0]
        aggregate_relationships = aggregates[1]
        aggregate_count = aggregates[2]

        reg["remuneration_total_int"] = aggregate_total
        reg["remuneration_total"] = self._format_number(aggregate_total)
        reg["interest_relationships"] = self._format_number(
            aggregate_relationships,
            currency=False
        )
        reg["remuneration_count"] = self._format_number(
            aggregate_count,
            currency=False
        )
        top_total, top_relationships, top_count = self._get_top(_db_table, reg_fields)
        reg["top"] = {
            "remuneration_total": self._format_top(top_total, "influencer"),
            "interest_relationships": self._format_top(
                top_relationships, "influencer", monetary=False
            ),
            "remuneration_count": self._format_top(
                top_count, "influencer", monetary=False
            )
        }

        # get lobby register data
        lobby_fields = ["lobbyists_hired"]
        aggregates = self._get_aggregate(_db_table, lobby_fields)
        lobby["lobbyists_hired"] = aggregates

        top_lobby = self._get_top(_db_table, lobby_fields)
        lobby["top"] = {
            "lobbyists_hired": self._format_top(
                top_lobby, "influencer", monetary=False
            ),
        }

        categories = {
            "electoral_commission": ec,
            "register_of_interests": reg,
            "lobby_registers": lobby,
            "meetings": meetings
        }
        result.update(categories)
        return result

    def _party_aggregate(self):
        _db_table = 'api_political_parties'
        result = {}

        result["count"] = self._format_number(self._db.count(_db_table), currency=False)

        ec_fields = ["donation_total_int", "donation_count"]
        aggregates = self._get_aggregate(_db_table, ec_fields)
        aggregate_total = aggregates[0]
        aggregate_count = aggregates[1]

        result["donation_total_int"] = aggregate_total
        result["donation_total"] = self._format_number(aggregate_total)
        result["donation_count"] = self._format_number(
            aggregate_count,
            currency=False
        )
        top_total, top_count = self._get_top(_db_table, ec_fields)
        result["top"] = {
            "donation_total": self._format_top(top_total, "party"),
            "donation_count": self._format_top(top_count, "party", monetary=False)
        }
        return result

    def _mp_aggregate(self):
        _db_table = 'api_mps'
        meetings, result, ec, reg = {}, {}, {}, {}

        result = {"count": self._db.count(_db_table)}

        # get meetings data
        meetings_fields = ["meetings_total"]
        aggregates = self._get_aggregate(_db_table, meetings_fields)
        aggregate_total = aggregates[0]
        meetings["meetings_total"] = self._format_number(aggregate_total, currency=False)
        top_total = self._get_top(_db_table, meetings_fields)
        meetings["top"] = {
            "meetings_total": self._format_top(top_total, "mp", monetary=False)
        }


        # get electoral commission data
        ec_fields = ["donation_total_int", "donor_count"]
        aggregates = self._get_aggregate(_db_table, ec_fields)
        aggregate_total = aggregates[0]
        aggregate_count = aggregates[1]
        ec["donation_total_int"] = aggregate_total
        ec["donation_total"] = self._format_number(aggregate_total, currency=False)
        ec["donor_count"] = self._format_number(aggregate_count, currency=False)
        top_total, top_count = self._get_top(_db_table, ec_fields)
        ec["top"] = {
            "donation_total": self._format_top(top_total, "mp"),
            "donor_count": self._format_top(top_count, "mp", monetary=False)
        }

        # get register of interests data
        reg_fields = [
            "remuneration_total_int",
            "lord_interest_relationships",
            "remuneration_count"
        ]
        aggregates = self._get_aggregate(_db_table, reg_fields)
        aggregate_total = aggregates[0]
        aggregate_relationships = aggregates[1]
        aggregate_count = aggregates[2]

        reg["remuneration_total_int"] = aggregate_total
        reg["remuneration_total"] = self._format_number(aggregate_total)
        reg["interest_relationships"] = self._format_number(
            aggregate_relationships,
            currency=False
        )
        reg["remuneration_count"] = self._format_number(
            aggregate_count,
            currency=False
        )
        top_total, top_relationships, top_count = self._get_top(_db_table, reg_fields)
        reg["top"] = {
            "remuneration_total": self._format_top(top_total, "mp"),
            "interest_relationships": self._format_top(
                top_relationships, "mp", monetary=False
            ),
            "remuneration_count": self._format_top(
                top_count, "mp", monetary=False
            )
        }
        categories = {
            "electoral_commission": ec,
            "register_of_interests": reg,
            "meetings": meetings
        }
        result.update(categories)
        return result

    def _lord_aggregate(self):
        _db_table = 'api_lords'
        meetings, result, ec, reg = {}, {}, {}, {}

        result = {"count": self._db.count(_db_table)}

        # get meetings data
        meetings_fields = ["meetings_total"]
        aggregates = self._get_aggregate(_db_table, meetings_fields)
        aggregate_total = aggregates[0]
        meetings["meetings_total"] = self._format_number(aggregate_total, currency=False)
        top_total = self._get_top(_db_table, meetings_fields)
        meetings["top"] = {
            "meetings_total": self._format_top(top_total, "lord", monetary=False)
        }

        # get electoral commission data
        ec_fields = ["donation_total_int", "donation_count"]
        aggregates = self._get_aggregate(_db_table, ec_fields)
        aggregate_total = aggregates[0]
        aggregate_count = aggregates[1]
        ec["donation_total_int"] = aggregate_total
        ec["donation_total"] = self._format_number(aggregate_total)
        ec["donation_count"] = self._format_number(aggregate_count, currency=False)
        top_total, top_count = self._get_top(_db_table, ec_fields)
        ec["top"] = {
            "donation_total": self._format_top(top_total, "lord"),
            "donation_count": self._format_top(top_count, "lord", monetary=False)
        }

        # get register of interests data
        reg_fields = ["lord_interest_relationships"]
        aggregate_relationships = self._get_aggregate(_db_table, reg_fields)[0]

        reg["interest_relationships"] = self._format_number(
            aggregate_relationships,
            currency=False
        )
        top_relationships = self._get_top(_db_table, reg_fields)
        reg["top"] = {
            "interest_relationships": self._format_top(
                top_relationships, "lord", monetary=False
            )
        }

        categories = {
            "electoral_commission": ec,
            "register_of_interests": reg,
            "meetings": meetings
            }
        result.update(categories)
        return result

    def _get_aggregate(self, table, field_list):
        return [self._db.sum(table, field=self.fields[x]) for x in field_list]

    def _get_top(self, table, field_list):
        result = [self._db.top(table, field=self.fields[x]) for x in field_list]
        return result[0] if len(result) == 1 else result

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
