from utils import mongo
from data_models import core, models


class PopulateMpsApi():
    def __init__(self):
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.api_mps
        self.data_models = models
        self.core_model = core.BaseDataModel()
        self.mps_graph = self.data_models.MembersOfParliament()
        self.all_mps = []

    def run(self):
        self.all_mps = self.mps_graph.get_all_mps()
        for doc in self.all_mps:
            name = doc[0]
            print name
            self._get_stats(doc)

    def _get_stats(self, record):
        register = {}
        ec = {}
        name = record[0]
        party = record[1]
        twfy_id = record[2]
        image_url = record[3]
        weight = record[4]
        register["remuneration_total"] = self._remuneration_total(name)
        register["interest_categories"] = self._interest_categories(name)
        register["interest_relationships"] = self._interest_relationships(name)
        register["remuneration_count"] = self._remuneration_count(name)
        register["interest_categories"] = self._interest_categories(name)
        ec["donor_count"] = self._donor_count(name)
        ec["donation_total"] = self._donation_total(name)
        positions = self._gov_positions(name)
        data_sources = {
            "register_of_interests": register,
            "electoral_commision": ec
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
        self.cache_data.save(mp_data)

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
            print positions
            return positions
        else:
            return None
