# -*- coding: utf-8 -*-
from flask import url_for


class BaseAPI:
    def __init__(self):
        pass

    @staticmethod
    def named_entity_resources(name, labels):
        api, web = None, None
        if name:
            if "mp" in labels or "Member of Parliament" in labels:
                #api = u"/api/v0.1/getMp?name={0}".format(name)
                api = url_for('getMp', name=name, _external=True)
                web = url_for('show_mp', name=name, _external=True)
            elif "lord" in labels or "Lord" in labels:
                #api = u"/api/v0.1/getLord?name={0}".format(name)
                api = url_for('getLord', name=name, _external=True)
                web = url_for('show_lord', name=name, _external=True)
            elif "party" in labels or "Political Party" in labels:
                #api = u"/api/v0.1/getPoliticalParty?name={0}".format(name)
                api = url_for('getPoliticalParty', name=name, _external=True)
                web = url_for('show_party', name=name, _external=True)
            elif "Lobby Agency" in labels and not "Lobby Agency Client" in labels:
                api = url_for('getLobbyAgency', name=name, _external=True)
                web = url_for('show_lobby_agency', name=name, _external=True)
            elif "influencer" in labels or "Donor" in labels \
                    or "Registered Interest" or "Lobby Agency Client" in labels:
                #api = u"/api/v0.1/getInfluencer?name={0}".format(name)
                api = url_for('getInfluencer', name=name, _external=True)
                web = url_for('show_influencer', name=name, _external=True)
            elif "Select Committee" in labels:
                api = url_for('getPoliticians', government_committee=name, _external=True)
                web = url_for('show_politicians', government_committee=name, _external=True)
            elif "Government Department" in labels:
                api = url_for('getPoliticians', government_department=name, _external=True)
                web = url_for('show_politicians', government_department=name, _external=True)
        return web, api

    @staticmethod
    def _nest_category(interests):
        categories = set([x["category"] for x in interests])
        category_entries = []
        for category in categories:
            entries = [x for x in interests if x["category"] == category]
            category_entries.append({"category": category, "interests": entries})
        return category_entries

    @staticmethod
    def _members_detail_url(members):
        if members:
            updated = []
            for member in members:
                entry = {
                    "name": member,
                    "detail_url": url_for(
                        'show_mp', name=member, _external=True
                    )
                }
                updated.append(entry)
            return updated
        else:
            return None

    @staticmethod
    def _committee_detail_urls(committees):
        if committees:
            updated = []
            for committee in committees:
                entry = {
                    "name": committee,
                    "detail_url": url_for(
                        'show_politicians_detail', government_committee=committee, _external=True
                    )
                }
                updated.append(entry)
            return updated
        else:
            return None

    @staticmethod
    def _department_detail_urls(departments):
        if departments:
            updated = []
            for dept in departments:
                entry = {
                    "name": dept,
                    "detail_url": url_for(
                        'show_politicians_detail', government_department=dept, _external=True
                    )
                }
                updated.append(entry)
            return updated
        else:
            return None

    @staticmethod
    def _get_members(record):
        result = None
        if "members" in record:
            result = record["members"]
        return result

    @staticmethod
    def _get_weight(record):
        result = None
        if "weight" in record:
            result = record["weight"]
        elif "mp_count" in record:
            result = record["mp_count"]
        return result

    @staticmethod
    def _fill_missing(field, record):
        result = None
        if field in record:
            result = record[field]
        return result

    @staticmethod
    def _format_number(number, currency=True):
        if isinstance(number, int):
            if currency:
                return u'£{:20,}'.format(number)
            else:
                return u'{:20,}'.format(number)
        else:
            return 0