# -*- coding: utf-8 -*-
from utils import mongo


class SummaryApi:
    def __init__(self):
        self._db = mongo.MongoInterface()

    def request(self):
        apis = {
            "political_parties": "http://127.0.0.1:5000/api/v0.1/getPoliticalParties",
            "influencers": "http://127.0.0.1:5000/api/v0.1/getInfluencers",
            "politicians": [
                "http://127.0.0.1:5000/api/v0.1/getMps",
                "http://127.0.0.1:5000/api/v0.1/getLords"
            ]
        }
        summary = {
            "influencers": self._influencers_aggregate(),
            "political_parties": self._party_aggregate(),
            "politicians": self._politician_aggregate()
        }
        content = {"summary": summary, "api_detail": apis}
        response = {
            "has_more": False,
            "page": 1,
            "per_page": 20,
            "content": content
        }
        return response

    def _party_aggregate(self):
        _db_table = 'api_political_parties'
        result = {"count": self._db.count(_db_table)}
        keys = ["donation_count", "donation_total_int"]
        fields = [
            '$influences.electoral_commission.donation_count',
            '$influences.electoral_commission.donation_total_int'
        ]
        values = [self._db.sum(_db_table, field=f) for f in fields]
        result.update(dict(zip(keys, values)))
        result["donation_total"] = _convert_to_currency(result["donation_total_int"])
        return result

    def _politician_aggregate(self):
        return {"mps": self._mp_aggregate(), "lords": self._lord_aggregate()}

    def _influencers_aggregate(self):
        categories = {}
        _db_table = 'api_influencers'
        result = {"count": self._db.count(_db_table)}

        # get electoral commission data
        ec_keys = ["donation_count", "donation_total_int"]
        ec_fields = [
            '$influences.electoral_commission.donation_count',
            '$influences.electoral_commission.donation_total_int'
        ]
        ec_values = [self._db.sum(_db_table, field=f) for f in ec_fields]
        categories["electoral_commission"] = dict(zip(ec_keys, ec_values))
        ec_display = _convert_to_currency(
            categories["electoral_commission"]["donation_total_int"]
        )
        categories["electoral_commission"]["donation_total"] = ec_display

        # get register of interests data
        reg_keys = [
            "interest_relationships", "remuneration_count", "remuneration_total_int"
        ]
        reg_fields = [
            '$influences.register_of_interests.relationship_count',
            '$influences.register_of_interests.remuneration_count',
            '$influences.register_of_interests.remuneration_total_int'
        ]
        reg_values = [self._db.sum(_db_table, field=f) for f in reg_fields]
        categories["register_of_interests"] = dict(zip(reg_keys, reg_values))
        reg_display = _convert_to_currency(
            categories["register_of_interests"]["remuneration_total_int"]
        )
        categories["register_of_interests"]["remuneration_total"] = reg_display
        result.update(categories)
        return result

    def _mp_aggregate(self):
        categories = {}
        _db_table = 'api_mps'
        result = {"count": self._db.count(_db_table)}

        # get electoral commission data
        ec_keys = ["donor_count", "donation_total_int"]
        ec_fields = [
            '$influences.electoral_commission.donor_count',
            '$influences.electoral_commission.donation_total_int'
        ]
        ec_values = [self._db.sum(_db_table, field=f) for f in ec_fields]
        categories["electoral_commission"] = dict(zip(ec_keys, ec_values))
        ec_display = _convert_to_currency(
            categories["electoral_commission"]["donation_total_int"]
        )
        categories["electoral_commission"]["donation_total"] = ec_display

        # get register of interests data
        reg_keys = [
            "interest_relationships", "remuneration_count", "remuneration_total_int"
        ]
        reg_fields = [
            '$influences.register_of_interests.interest_relationships',
            '$influences.register_of_interests.remuneration_count',
            '$influences.register_of_interests.remuneration_total_int'
        ]
        reg_values = [self._db.sum(_db_table, field=f) for f in reg_fields]
        categories["register_of_interests"] = dict(zip(reg_keys, reg_values))
        reg_display = _convert_to_currency(
            categories["register_of_interests"]["remuneration_total_int"]
        )
        categories["register_of_interests"]["remuneration_total"] = reg_display
        result.update(categories)
        return result

    def _lord_aggregate(self):
        categories = {}
        _db_table = 'api_lords'
        result = {"count": self._db.count(_db_table)}

        # get electoral commission data
        ec_keys = ["donation_count", "donation_total_int"]
        ec_fields = [
            '$influences.electoral_commission.donation_count',
            '$influences.electoral_commission.donation_total_int'
        ]
        ec_values = [self._db.sum(_db_table, field=f) for f in ec_fields]
        categories["electoral_commission"] = dict(zip(ec_keys, ec_values))
        ec_display = _convert_to_currency(
            categories["electoral_commission"]["donation_total_int"]
        )
        categories["electoral_commission"]["donation_total"] = ec_display

        # get register of interests data
        reg_keys = ["interest_relationships"]
        reg_fields = [
            '$influences.register_of_interests.interest_relationships'
        ]
        reg_values = [self._db.sum(_db_table, field=f) for f in reg_fields]
        categories["register_of_interests"] = dict(zip(reg_keys, reg_values))
        result.update(categories)
        return result


def _convert_to_currency(number):
    if isinstance(number, int):
        return u'£{:20,.2f}'.format(number)
    else:
        return 0