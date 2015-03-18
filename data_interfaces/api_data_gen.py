# -*- coding: utf-8 -*-
import logging
from utils import mongo
from data_models.influencers_models import Influencer
from data_models.influencers_models import Influencers
from data_models.influencers_models import LobbyAgency
from data_models.influencers_models import LobbyAgencies
from data_models import government_models


class PopulateLobbyAgenciesApi():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()

    def run(self):
        self.db.drop("api_lobbyists")
        all_agencies = LobbyAgencies().get_all()
        self._logger.debug("Populating Lobby Agencies Api")
        for doc in all_agencies:
            name = doc[0]
            self._logger.debug(name)
            self._get_stats(doc)

    def _get_stats(self, record):
        name = record[0]
        clients = record[1]
        employees = record[2]
        labels = record[3]
        if labels and "Named Entity" in labels:
            labels.remove("Named Entity")

        data_sources = {
            "lobbying_registers": {
                "client_count": clients,
                "employee_count": employees
            }
        }
        agency_data = {
            "name": name,
            "influences": data_sources,
            "labels": labels
        }
        self.db.save("api_lobbyists", agency_data)


class PopulatePoliticiansApi():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()

    def run(self):
        self.db.drop("api_politicians")
        all_politicians = government_models.Politicians().get_all()
        self._logger.debug("Populating Politicians Api")
        for doc in all_politicians:
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

        politician = government_models.Politician(name)
        if not politician.exists:
            print ">Not found:", name
            politician = government_models.Lord(name)
            role = "lord"
        else:
            role = politician.type
        register = politician.interests_summary
        ec = politician.donations_summary

        data_sources = {
            "register_of_interests": register,
            "electoral_commission": ec
        }
        politician_data = {
            "name": name,
            "type": role,
            "party": party,
            "twfy_id": twfy_id,
            "weight": weight,
            "image_url": image_url,
            "influences": data_sources,
            "labels": labels
        }

        if role == "mp":
            politician_data["government_departments"] = politician.departments
            politician_data["government_positions"] = politician.positions
        else:
            politician_data["government_departments"] = None
            politician_data["government_positions"] = None

        self.db.save("api_politicians", politician_data)


class PopulateMpsApi():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()

    def run(self):
        self.db.drop("api_mps")
        all_mps = government_models.MembersOfParliament().get_all()
        self._logger.debug("Populating MPs Api")
        for doc in all_mps:
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

        mp = government_models.MemberOfParliament(name)
        positions = mp.positions
        departments = mp.departments
        register = mp.interests_summary
        ec = mp.donations_summary

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
        self.db.save("api_mps", mp_data)


class PopulateLordsApi():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()

    def run(self):
        self.db.drop("api_lords")
        all_lords = government_models.Lords().get_all()
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

        lord = government_models.Lord(name)
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
        self.db.save("api_lords", lord_data)


class PopulateInfluencersApi():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()

    def run(self):
        self.db.drop("api_influencers")
        all_influencers = Influencers().get_all()
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

        influencer = Influencer(name)
        register = influencer.interests_summary
        ec = influencer.donations_summary
        lobby = influencer.lobbyists_summary

        data_sources = {}
        if register["relationship_count"] > 0:
            data_sources["register_of_interests"] = register
        if ec["donation_count"] > 0:
            data_sources["electoral_commission"] = ec
        if lobby["lobbyist_hired"] > 0:
            data_sources["lobby_registers"] = lobby
        influencer_data = {
            "name": name,
            "labels": labels,
            "weight": weight,
            "donor_type": donor_type,
            "influences": data_sources
        }
        self.db.save("api_influencers", influencer_data)


class PopulatePoliticalPartyApi():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()

    def run(self):
        self.db.drop("api_political_parties")
        all_parties = government_models.PoliticalParties().get_all()
        self._logger.debug("Populating Political Party Api")
        for doc in all_parties:
            name = doc[0]
            self._logger.debug(name)
            self._get_stats(doc)

    def _get_stats(self, record):
        name = record[0]
        image_url = record[1]
        weight = record[2]

        party = government_models.PoliticalParty(name)
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
        self.db.save("api_political_parties", party_data)


class PopulateDepartmentsApi():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.db = mongo.MongoInterface()

    def run(self):
        self.db.drop("api_government")
        all_offices = government_models.GovernmentOffices().get_all()

        self._logger.debug("Populating Government Offices Api")
        for doc in all_offices:
            name = doc[0]
            self._logger.debug("%s, %s" % (name, doc[2]))
            self._get_stats(doc)

    def _get_stats(self, record):
        name = record[0]
        labels = record[1]
        mp_count = record[2]

        if labels and "Named Entity" in labels:
            labels.remove("Named Entity")
            labels.remove("Government Office")

        office = government_models.GovernmentOffice(name)
        members = office.members
        register = office.interests_summary
        ec = office.donation_summary

        data_sources = {
            "register_of_interests": register,
            "electoral_commission": ec
        }

        office_data = {
            "name": name,
            "labels": labels,
            "mp_count": mp_count,
            "influences": data_sources,
            "members": members
        }
        self.db.save("api_government", office_data)


def _convert_to_currency(number):
    if isinstance(number, int):
        return u'£{:20,.2f}'.format(number)
    else:
        return 0
