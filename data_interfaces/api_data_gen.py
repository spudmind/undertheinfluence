# -*- coding: utf-8 -*-
import logging
from utils import mongo
from data_models import core, models


class PopulateMpsApi():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.cache = mongo.MongoInterface()
        self.core_model = core.BaseDataModel()
        self.mps_graph = models.MembersOfParliament()
        self.all_mps = []

    def run(self):
        self.cache.drop("api_mps")
        self.all_mps = self.mps_graph.get_all()
        self._logger.debug("Populating MPs Api")
        for doc in self.all_mps:
            name = doc[0]
            self._logger.debug(name)
            self._get_stats(doc)

    def _get_stats(self, record):
        name = record[0]
        party = record[1]
        twfy_id = record[2]
        image_url = record[3]
        weight = record[4]
        labels = record[5]
        if labels and "Named Entity" in labels:
            labels.remove("Named Entity")

        mp = models.MemberOfParliament(name)
        register = mp.interests_summary
        ec = mp.donations_summary
        departments = mp.departments
        positions = mp.positions

        data_sources = {
            "register_of_interests": register,
            "electoral_commission": ec
        }
        mp_data = {
            "name": name,
            "party": party,
            "twfy_id": twfy_id,
            "weight": weight,
            "image_url": image_url,
            "influences": data_sources,
            "labels": labels,
            "government_departments": departments,
            "government_positions": positions
        }
        self.cache.save("api_mps", mp_data)


class PopulateLordsApi():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.cache = mongo.MongoInterface()
        self.core_model = core.BaseDataModel()
        self.lords_graph = models.Lords()

    def run(self):
        self.cache.drop("api_lords")
        all_lords = self.lords_graph.get_all()
        self._logger.debug("Populating  Lords Api")
        for doc in all_lords:
            name = doc[0]
            self._logger.debug(name)
            self._get_stats(doc)

    def _get_stats(self, record):
        name = record[0]
        party = record[1]
        twfy_id = record[2]
        weight = record[3]
        labels = record[4]
        if labels and "Named Entity" in labels:
            labels.remove("Named Entity")

        lord = models.Lord(name)
        register = lord.interests_summary
        ec = lord.donations_summary

        data_sources = {}
        if register["interest_categories"] > 0 and register["interest_relationships"] > 0:
            data_sources["register_of_interests"] = register
        if ec["donation_total_int"] > 0 and ec["donation_count"] > 0:
            data_sources["electoral_commission"] = ec
        lord_data = {
            "name": name,
            "party": party,
            "twfy_id": twfy_id,
            "weight": weight,
            "labels": labels,
            "influences": data_sources
        }
        self.cache.save("api_lords", lord_data)


class PopulateInfluencersApi():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.cache = mongo.MongoInterface()
        self.core_model = core.BaseDataModel()
        self.influencers_graph = models.Influencers()

    def run(self):
        self.cache.drop("api_influencers")
        all_influencers = self.influencers_graph.get_all()
        self._logger.debug("\nPopulating Influencers Api")
        self._logger.debug("Total: %s" % len(all_influencers))
        for doc in all_influencers:
            self._logger.debug("%s - %s" % (doc[0], doc[1]))
            self._get_stats(doc)

    def _get_stats(self, record):
        name = record[0]
        donor_type = record[1]
        labels = record[2]
        weight = record[3]
        if labels and "Named Entity" in labels:
            labels.remove("Named Entity")

        influencer = models.Influencer(name)
        register = influencer.interests_summary
        ec = influencer.donations_summary

        data_sources = {}
        if register["relationship_count"] > 0:
            data_sources["register_of_interests"] = register
        if ec["donation_count"] > 0:
            data_sources["electoral_commission"] = ec
        influencer_data = {
            "name": name,
            "labels": labels,
            "weight": weight,
            "donor_type": donor_type,
            "influences": data_sources
        }
        self.cache.save("api_influencers", influencer_data)


class PopulatePoliticalPartyApi():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.cache = mongo.MongoInterface()
        self.core_model = core.BaseDataModel()
        self.parties_graph = models.PoliticalParties()

    def run(self):
        self.cache.drop("api_political_parties")
        all_parties = self.parties_graph.get_all()
        self._logger.debug("Populating Political Party Api")
        for doc in all_parties:
            name = doc[0]
            self._logger.debug(name)
            self._get_stats(doc)

    def _get_stats(self, record):
        name = record[0]
        image_url = record[1]
        weight = record[2]

        party = models.PoliticalParty(name)
        ec = party.donations_summary
        mp_count = party.mp_count
        lord_count = party.lord_count

        data_sources = {}
        if ec["donation_total_int"] > 0 and ec["donation_count"] > 0:
            data_sources["electoral_commission"] = ec

        party_data = {
            "name": name,
            "weight": weight,
            "mp_count": mp_count,
            "lord_count": lord_count,
            "influences": data_sources,
            "image_url": image_url
        }
        print party_data
        self.cache.save("api_political_parties", party_data)


def _convert_to_currency(number):
    if isinstance(number, int):
        return u'£{:20,.2f}'.format(number)
    else:
        return 0
