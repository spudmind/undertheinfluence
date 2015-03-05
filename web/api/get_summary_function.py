# -*- coding: utf-8 -*-
from utils import mongo
from flask import url_for


class SummaryApi:
    def __init__(self):
        self._db = mongo.MongoInterface()

    def request(self):
        apis = {
            "political_parties": url_for('getPoliticalParties', _external=True),
            "influencers": url_for('getInfluencers', _external=True),
            "politicians": url_for('getPoliticians', _external=True),
            "government_departments": url_for('getGovernmentDepartments', _external=True),
        }
        summary = {
            "influencers": self._influencers_aggregate(),
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

    def _party_aggregate(self):
        _db_table = 'api_political_parties'
        result = {}

        donation_count = "$influences.electoral_commission.donation_count"
        donation_total_int = "$influences.electoral_commission.donation_total_int"

        result["count"] = _format_number(self._db.count(_db_table), currency=False)
        result["donation_total_int"] = self._db.sum(_db_table, field=donation_total_int)
        result["donation_count"] = _format_number(
            self._db.sum(_db_table, field=donation_count), currency=False
        )
        result["donation_total"] = _format_number(
            self._db.sum(_db_table, field=donation_total_int)
        )
        return result

    def _influencers_aggregate(self):
        _db_table = 'api_influencers'
        categories, result, ec, reg = {}, {}, {}, {}

        result["count"] = _format_number(self._db.count(_db_table), currency=False)

        # get electoral commission data
        donation_count = "$influences.electoral_commission.donation_count"
        donation_total_int = "$influences.electoral_commission.donation_total_int"

        ec["donation_total_int"] = self._db.sum(_db_table, field=donation_total_int)
        ec["donation_count"] = _format_number(
            self._db.sum(_db_table, field=donation_count), currency=False
        )
        ec["donation_total"] = _format_number(
            self._db.sum(_db_table, field=donation_total_int)
        )
        categories["electoral_commission"] = ec

        # get register of interests data
        interest_relationships = "$influences.register_of_interests.relationship_count"
        remuneration_count = '$influences.register_of_interests.remuneration_count'
        remuneration_total_int = '$influences.register_of_interests.remuneration_total_int'

        reg["remuneration_total_int"] = self._db.sum(
            _db_table, field=remuneration_total_int
        )
        reg["remuneration_total"] = _format_number(
            self._db.sum(_db_table, field=remuneration_total_int)
        )
        reg["interest_relationships"] = _format_number(
            self._db.sum(_db_table, field=interest_relationships), currency=False
        )
        reg["remuneration_count"] = _format_number(
            self._db.sum(_db_table, field=remuneration_count), currency=False
        )
        categories["register_of_interests"] = reg

        result.update(categories)
        return result

    def _mp_aggregate(self):
        _db_table = 'api_mps'
        categories, result, ec, reg = {}, {}, {}, {}

        result = {"count": self._db.count(_db_table)}

        # get electoral commission data
        donor_count = '$influences.electoral_commission.donor_count'
        donation_total_int = '$influences.electoral_commission.donation_total_int'

        ec["donation_total_int"] = self._db.sum(_db_table, field=donation_total_int)
        ec["donation_total"] = _format_number(
            self._db.sum(_db_table, field=donation_total_int)
        )
        ec["donor_count"] = _format_number(
            self._db.sum(_db_table, field=donor_count), currency=False
        )
        categories["electoral_commission"] = ec

        # get register of interests data

        interest_relationships = "$influences.register_of_interests.interest_relationships"
        remuneration_count = '$influences.register_of_interests.remuneration_count'
        remuneration_total_int = '$influences.register_of_interests.remuneration_total_int'

        reg["remuneration_total_int"] = self._db.sum(
            _db_table, field=remuneration_total_int
        )
        reg["remuneration_total"] = _format_number(
            self._db.sum(_db_table, field=remuneration_total_int)
        )
        reg["interest_relationships"] = _format_number(
            self._db.sum(_db_table, field=interest_relationships), currency=False
        )
        reg["remuneration_count"] = _format_number(
            self._db.sum(_db_table, field=remuneration_count), currency=False
        )
        categories["register_of_interests"] = reg

        result.update(categories)
        return result

    def _lord_aggregate(self):
        _db_table = 'api_lords'
        categories, result, ec, reg = {}, {}, {}, {}

        result = {"count": self._db.count(_db_table)}

        # get electoral commission data

        donation_count = "$influences.electoral_commission.donation_count"
        donation_total_int = "$influences.electoral_commission.donation_total_int"

        ec["donation_total_int"] = self._db.sum(_db_table, field=donation_total_int)
        ec["donation_count"] = _format_number(
            self._db.sum(_db_table, field=donation_count), currency=False
        )
        ec["donation_total"] = _format_number(
            self._db.sum(_db_table, field=donation_total_int)
        )
        categories["electoral_commission"] = ec

        # get register of interests data
        interest_relationships = '$influences.register_of_interests.interest_relationships'
        reg["interest_relationships"] = _format_number(
            self._db.sum(_db_table, field=interest_relationships), currency=False
        )
        categories["register_of_interests"] = reg

        result.update(categories)
        return result


def _format_number(number, currency=True):
    if isinstance(number, int):
        if currency:
            return u'£{:20,}'.format(number)
        else:
            return u'{:20,}'.format(number)
    else:
        return 0