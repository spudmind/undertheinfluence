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
        self.all_mps = self.mps_graph.get_all()
        self._logger.debug("Populating MPs Api")
        for doc in self.all_mps:
            name = doc[0]
            self._logger.debug(name)
            self._get_stats(doc)

    def _get_stats(self, record):
        register = {}
        ec = {}
        name = record[0]
        party = record[1]
        twfy_id = record[2]
        image_url = record[3]
        weight = record[4]
        register["remuneration_total"] = _convert_to_currency(
            self._remuneration_total(name)
        )
        register["remuneration_total_int"] = self._remuneration_total(name)
        register["interest_categories"] = self._interest_categories(name)
        register["interest_relationships"] = self._interest_relationships(name)
        register["remuneration_count"] = self._remuneration_count(name)
        ec["donor_count"] = self._donor_count(name)
        ec["donation_total"] = _convert_to_currency(
            self._donation_total(name)
        )
        ec["donation_total_int"] = self._donation_total(name)
        positions = self._gov_positions(name)
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
            "government_positions": positions
        }
        self.cache.save("api_mps", mp_data)

    def _remuneration_total(self, name):
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}}) WITH mp
            MATCH (mp)-[:INTERESTS_REGISTERED_IN]-(cat) with mp, cat
            MATCH (cat)-[x:INTEREST_RELATIONSHIP]-(rel) with mp, cat, rel
            MATCH (rel)-[y:REMUNERATION_RECEIVED]-(x)
            RETURN sum(x.amount) as total
        """.format(name)
        return self.core_model.query(query)[0]["total"]

    def _interest_categories(self, name):
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}}) WITH mp
            MATCH (mp)-[:INTERESTS_REGISTERED_IN]-(cat) with mp, cat
            RETURN count(cat) as category_count
        """.format(name)
        return self.core_model.query(query)[0]["category_count"]

    def _interest_relationships(self, name):
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}}) WITH mp
            MATCH (mp)-[:INTERESTS_REGISTERED_IN]-(cat) with mp, cat
            MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel) with mp, cat, rel
            RETURN count(rel) as relationship_count
        """.format(name)
        return self.core_model.query(query)[0]["relationship_count"]

    def _remuneration_count(self, name):
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}}) WITH mp
            MATCH (mp)-[:INTERESTS_REGISTERED_IN]-(cat) with mp, cat
            MATCH (cat)-[x:INTEREST_RELATIONSHIP]-(rel) with mp, cat, rel
            MATCH (rel)-[y:REMUNERATION_RECEIVED]-(x)
            RETURN count(x) as remuneration_count
        """.format(name)
        return self.core_model.query(query)[0]["remuneration_count"]

    def _donor_count(self, name):
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}}) WITH mp
            MATCH (mp)-[:FUNDING_RELATIONSHIP]-(rel) with mp, rel
            RETURN DISTINCT count(rel.donor) as donor_count
        """.format(name)
        return self.core_model.query(query)[0]["donor_count"]

    def _donation_total(self, name):
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}}) WITH mp
            MATCH (mp)-[:FUNDING_RELATIONSHIP]-(rel) with mp, rel
            MATCH (rel)-[y:DONATION_RECEIVED]-(x)
            RETURN sum(x.amount) as total
        """.format(name)
        return self.core_model.query(query)[0]["total"]

    def _gov_positions(self, name):
        positions = []
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}}) with mp
            MATCH (mp)-[:ELECTED_FOR]-(term) with mp, term
            MATCH (term)-[:SERVED_IN]-(pos) with mp, term, pos
            RETURN DISTINCT pos.name as positions
        """.format(name)
        results = self.core_model.query(query)
        if results:
            for result in results:
                positions.append(result["positions"])
            self._logger.debug(positions)
            return positions
        else:
            return None


class PopulateLordsApi():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.cache = mongo.MongoInterface()
        self.core_model = core.BaseDataModel()
        self.lords_graph = models.Lords()

    def run(self):
        all_lords = self.lords_graph.get_all()
        self._logger.debug("Populating  Lords Api")
        for doc in all_lords:
            name = doc[0]
            self._logger.debug(name)
            self._get_stats(doc)

    def _get_stats(self, record):
        register = {}
        ec = {}
        name = record[0]
        party = record[1]
        twfy_id = record[2]
        weight = record[3]
        register["interest_relationships"] = self._interest_relationships(name)
        register["interest_categories"] = self._interest_categories(name)
        ec["donation_count"] = self._donation_count(name)
        ec["donation_total"] = _convert_to_currency(self._donation_total(name))
        ec["donation_total_int"] = self._donation_total(name)
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
            "influences": data_sources
        }
        self.cache.save("api_lords", lord_data)

    def _interest_categories(self, name):
        query = u"""
            MATCH (lord:`Lord` {{name: "{0}"}}) WITH lord
            MATCH (lord)-[:INTERESTS_REGISTERED_IN]-(cat) with lord, cat
            RETURN count(cat) as category_count
        """.format(name)
        return self.core_model.query(query)[0]["category_count"]

    def _interest_relationships(self, name):
        query = u"""
            MATCH (lord:`Lord` {{name: "{0}"}}) WITH lord
            MATCH (lord)-[:INTERESTS_REGISTERED_IN]-(cat) with lord, cat
            MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel) with lord, cat, rel
            RETURN count(rel) as relationship_count
        """.format(name)
        return self.core_model.query(query)[0]["relationship_count"]

    def _donation_count(self, name):
        query = u"""
            MATCH (lord:`Lord` {{name: "{0}"}}) WITH lord
            MATCH (lord)-[x:REGISTERED_CONTRIBUTOR]-() with x
            RETURN count(x) as donation_count
        """.format(name)
        return self.core_model.query(query)[0]["donation_count"]

    def _donation_total(self, name):
        query = u"""
            MATCH (lord:`Lord` {{name: "{0}"}}) WITH lord
            MATCH (lord)-[:REGISTERED_CONTRIBUTOR]-(rel) with lord, rel
            MATCH (rel)-[:DONATION_RECEIVED]-(x)
            RETURN sum(x.amount) as total
        """.format(name)
        return self.core_model.query(query)[0]["total"]


class PopulateInfluencersApi():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.cache = mongo.MongoInterface()
        self.core_model = core.BaseDataModel()
        self.influencers_graph = models.Influencers()

    def run(self):
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
        if labels and "Named Entity" in labels:
            labels.remove("Named Entity")
        weight = record[3]
        register = {}
        ec = {}
        register["relationship_count"] = self._interest_relationships(name)

        register["remuneration_total"] = _convert_to_currency(
            self._remuneration_total(name)
        )
        register["remuneration_total_int"] = self._remuneration_total(name)
        register["remuneration_count"] = self._remuneration_count(name)
        ec["donation_count"] = self._donation_count(name)
        ec["donation_total"] = _convert_to_currency(
            self._donation_total(name)
        )
        ec["donation_total_int"] = self._donation_total(name)
        ec["donor_type"] = donor_type
        data_sources = {}
        if register["relationship_count"] > 0:
            data_sources["register_of_interests"] = register
        if ec["donation_count"] > 0:
            data_sources["electoral_commission"] = ec
        influencer_data = {
            "name": name,
            "labels": labels,
            "weight": weight,
            "influences": data_sources
        }
        self.cache.save("api_influencers", influencer_data)

    def _donation_total(self, name):
        query = u"""
            MATCH (inf:`Named Entity` {{name: "{0}"}})
            MATCH (inf)-[:REGISTERED_CONTRIBUTOR]-(rel)
            MATCH (rel)-[:DONATION_RECEIVED]-(x)
            RETURN sum(x.amount) as total
        """.format(name)
        return self.core_model.query(query)[0]["total"]

    def _donation_count(self, name):
        query = u"""
            MATCH (inf:`Named Entity` {{name: "{0}"}})
            MATCH (inf)-[:REGISTERED_CONTRIBUTOR]-(rel)
            MATCH (rel)-[:DONATION_RECEIVED]-(x)
            RETURN count(x) as count
        """.format(name)
        return self.core_model.query(query)[0]["count"]

    def _interest_relationships(self, name):
        query = u"""
            MATCH (inf:`Named Entity` {{name: "{0}"}})
            MATCH (inf)-[:REGISTERED_CONTRIBUTOR]-(rel)
            MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel)
            RETURN count(rel) as count
        """.format(name)
        return self.core_model.query(query)[0]["count"]

    def _remuneration_total(self, name):
        query = u"""
            MATCH (inf:`Named Entity` {{name: "{0}"}})
            MATCH (inf)-[:REGISTERED_CONTRIBUTOR]-(rel)
            MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel)
            MATCH (rel)-[:REMUNERATION_RECEIVED]-(x)
            RETURN sum(x.amount) as total
        """.format(name)
        return self.core_model.query(query)[0]["total"]

    def _remuneration_count(self, name):
        query = u"""
            MATCH (inf:`Named Entity` {{name: "{0}"}})
            MATCH (inf)-[:REGISTERED_CONTRIBUTOR]-(rel)
            MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel)
            MATCH (rel)-[:REMUNERATION_RECEIVED]-(x)
            RETURN count(x) as count
        """.format(name)
        return self.core_model.query(query)[0]["count"]


class PopulatePoliticalPartyApi():
    def __init__(self):
        self._logger = logging.getLogger('spud')
        self.cache = mongo.MongoInterface()
        self.core_model = core.BaseDataModel()
        self.parties_graph = models.PoliticalParties()

    def run(self):
        all_parties = self.parties_graph.get_all()
        self._logger.debug("Populating Political Party Api")
        for doc in all_parties:
            name = doc[0]
            self._logger.debug(name)
            self._get_stats(doc)

    def _get_stats(self, record):
        ec = {}
        name = record[0]
        weight = record[1]
        total, count = self._donations(name)
        ec["donation_count"] = count
        ec["donation_total"] = _convert_to_currency(total)
        ec["donation_total_int"] = total
        mp_count = self._mp_count(name)
        lord_count = self._lord_count(name)
        data_sources = {}
        if ec["donation_total_int"] > 0 and ec["donation_count"] > 0:
            data_sources["electoral_commission"] = ec
        party_data = {
            "name": name,
            "weight": weight,
            "mp_count": mp_count,
            "lord_count": lord_count,
            "influences": data_sources
        }
        self.cache.save("api_political_parties", party_data)

    def _mp_count(self, name):
        query = u"""
            MATCH (p:`Political Party` {{name: "{0}"}})
            MATCH (mp:`Member of Parliament`)-[:MEMBER_OF]-(p)
            RETURN count(mp) as mp_count
        """.format(name)
        return self.core_model.query(query)[0]["mp_count"]

    def _lord_count(self, name):
        query = u"""
            MATCH (p:`Political Party` {{name: "{0}"}})
            MATCH (l:`Lord`)-[:MEMBER_OF]-(p)
            RETURN count(l) as lord_count
        """.format(name)
        return self.core_model.query(query)[0]["lord_count"]

    def _donations(self, name):
        query = u"""
            MATCH (p:`Political Party` {{name: "{0}"}})
            MATCH (p)-[:FUNDING_RELATIONSHIP]-(x)
            MATCH (x)-[:DONATION_RECEIVED]-(f)
            RETURN p.name as Party, sum(f.amount) as total, count(f.amount) as count
            ORDER BY total DESC
        """.format(name)
        output = self.core_model.query(query)
        if output:
            return output[0]["total"], output[0]["count"]
        else:
            return 0, 0


def _convert_to_currency(number):
    if isinstance(number, int):
        return u'£{:20,.2f}'.format(number)
    else:
        return 0
