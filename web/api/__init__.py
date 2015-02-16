from flask import url_for


class BaseAPI:
    def __init__(self):
        pass

    @staticmethod
    def named_entity_resources(name, labels):
        api, web = None, None
        if "Member of Parliament" in labels:
            api = u"/api/v0.1/getMp?name={0}".format(name)
            web = url_for('show_mp', name=name, _external=True)
        elif "Lord" in labels:
            api = u"/api/v0.1/getLord?name={0}".format(name)
            web = url_for('show_lord', name=name, _external=True)
        elif "Donor" in labels or "Registered Interest" in labels:
            api = u"/api/v0.1/getInfluencer?name={0}".format(name)
            web = url_for('show_influencer', name=name, _external=True)
        elif "Political Party" in labels:
            api = u"/api/v0.1/getPoliticalParty?name={0}".format(name)
            web = url_for('show_party', name=name, _external=True)
        return web, api

    @staticmethod
    def _nest_category(interests):
        categories = set([x["category"] for x in interests])
        category_entries = []
        for category in categories:
            entries = [x for x in interests if x["category"] == category]
            category_entries.append({"category": category, "interests": entries})
        return category_entries