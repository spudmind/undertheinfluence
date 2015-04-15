# -*- coding: utf-8 -*-
from data_models.core import BaseDataModel
from data_models.core import NamedEntity
from utils import config


class Politicians(BaseDataModel):
    def __init__(self):
        BaseDataModel.__init__(self)
        self.count = self._get_count()

    def get_all(self):
        search_string = u"""
            MATCH (p) where p:Lord OR p:`Member of Parliament` with p
            MATCH (p)-[r]-() with p,  r
            RETURN DISTINCT p.name, p.party, p.twfy_id, p.image,
                count(r) as weight, labels(p)
            ORDER BY weight DESC
        """
        search_result = self.query(search_string)
        return search_result

    def _get_count(self):
        search_string = u"""
            MATCH (p) where p:Lord OR p:`Member of Parliament` with p
            RETURN count(p)
        """
        search_result = self.query(search_string)
        return search_result[0][0]


class Politician(NamedEntity):
    def __init__(self, name=None):
        NamedEntity.__init__(self)
        self.label = "Named Entity"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.name
        )
        if self.exists:
            self.labels = self._get_labels()
            self.type = self._get_type()
            self._set_properties()

    def _get_type(self):
        if "Member of Parliament" in self.labels:
            return "mp"
        elif "Lord" in self.labels:
            return "lord"

    def _set_properties(self):
        if self.type == "mp":
            politician = MemberOfParliament(self.name)
            self.positions = politician.positions
            self.committees = politician.committees
        elif self.type == "lord":
            politician = Lord(self.name)
        else:
            print "something wrong with:", self.name
        self.meetings = politician.meetings
        self.meetings_summary = politician.meetings_summary
        self.interests = politician.interests
        self.interests_summary = politician.interests_summary
        self.donations = politician.donations
        self.donations_summary = politician.donations_summary

    def _get_labels(self):
        query = u"""
            MATCH (p:`Named Entity` {{name: "{0}"}}) WITH p
            RETURN labels(p) as labels
        """.format(self.vertex["name"])
        return self.query(query)[0][0]


class MembersOfParliament(BaseDataModel):
    def __init__(self):
        BaseDataModel.__init__(self)
        self.count = self._get_mp_count()

    def get_all(self):
        search_string = u"""
            MATCH (mp:`Member of Parliament`) with mp
            MATCH (mp)-[r]-() with mp,  r
            RETURN mp.name, mp.party, mp.twfy_id, mp.image,
                count(r) as weight, labels(mp) as labels
            ORDER BY weight DESC
        """
        search_result = self.query(search_string)
        return search_result

    def _get_mp_count(self):
        search_string = u"""
            MATCH (mp:`Member of Parliament`)
            RETURN count(mp)
        """
        search_result = self.query(search_string)
        return search_result[0][0]


class MemberOfParliament(NamedEntity):
    def __init__(self, name=None, get_properties=True):
        NamedEntity.__init__(self)
        self.label = "Member of Parliament"
        self.primary_attribute = "name"
        self.name = name
        self._get_properties = get_properties
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.name
        )
        if self.exists and self._get_properties:
            self.party, self.image_url = self._set_properties()
            self.positions = self._get_positions()
            self.committees = self._get_committees()
            self.meetings = self._get_meetings()
            self.meetings_summary = self._get_meeting_summary()
            self.interest_categories = self._interest_categories()
            self.interests = self._get_interests()
            self.interests_summary = self._get_interests_summary()
            self.donations = self._get_donations()
            self.donations_summary = self._get_donations_summary()

    def _get_positions(self):
        return self._get_government_positions("Government Position")

    def _get_committees(self):
        return self._get_government_positions("Government Committee")

    def _set_properties(self):
        search_string = u"""
            MATCH (mp:`Member of Parliament` {{name:"{0}"}})
            return mp.party, mp.image
        """.format(self.vertex["name"])
        output = self.query(search_string)
        return output[0]["mp.party"], output[0]["mp.image"]

    def _get_government_positions(self, pos_type):
        results = []
        search_string = u"""
            MATCH (mp:`Member of Parliament` {{name:"{0}"}}) with mp
            MATCH (mp)-[:ELECTED_FOR]-(const) with const
                WHERE const.left_reason = "still_in_office"
                    OR const.left_reason = "general_election"
            MATCH (const)-[:SERVED_IN]-(p:`{1}`) with p.name AS position
            RETURN position
        """.format(self.vertex["name"], pos_type)
        output = self.query(search_string)
        for entry in output:
            results.append(entry[0])
        return results

    def _get_meeting_summary(self):
        results = []
        meetings = {"meetings_total": 0}
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}})
            MATCH (mp)-[:SERVED_IN]-(p:`Government Office`) with mp, p
            MATCH (p)-[:ATTENDED_BY]-(m) with mp, p, m
                WHERE m.host_name = "{0}"
            MATCH (m)-[:ATTENDED_BY]-(a:`Meeting Attendee`) with mp, p, m, a
            RETURN p.name, count(a), collect(a.name)
        """.format(self.vertex["name"])
        output = self.query(query)
        for entry in output:
            results.append(
                {
                    "position": entry[0],
                    "meetings_count": entry[1],
                    "influencers_met": list(set(entry[2]))
                }
            )
        meetings["meetings_total"] = sum(m['meetings_count'] for m in results)
        meetings["meetings_per_position"] = results
        return meetings

    def _get_meetings(self):
        results = []
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}})
            MATCH (mp)-[:SERVED_IN]-(p:`Government Office`) with mp, p
            MATCH (p)-[:ATTENDED_BY]-(m) with mp, p, m
                WHERE m.host_name = "{0}"
            MATCH (m)-[:ATTENDED_BY]-(a:`Meeting Attendee`) with mp, p, m, a
            RETURN p.name as position, a.name as attendee, m.meeting as meeting,
                m.purpose as purpose, m.date as date
            ORDER BY date
        """.format(self.vertex["name"])
        output = self.query(query)
        for entry in output:
            meeting = {
                "position": entry["position"],
                "attendee": entry["attendee"],
                "purpose": entry["purpose"],
                "meeting": entry["meeting"],
                "date": entry["date"],
            }
            results.append(meeting)
        return results

    def _get_interests(self):
        common = [
            "contributor",
            "source_url",
            "source_fetched",
            "source_linked_from",
            "recipient",
            "`recorded date`",
            "registered"
        ]
        category_fields = {
            "directorships": common,
            "remunerated directorships": common,
            # "Clients": common,
            "shareholdings": common,
            "registrable shareholdings": common,
            "sponsorships": common + ["amount", "donor_status"],
            "overseas visits": common + ["amount", "visit_dates", "purpose"],
            "miscellaneous": common,
            "miscellaneous and unremunerated interests": common,
            "sponsorship or financial or material support":
                common + ["amount", "donor_status"],
            "gifts, benefits and hospitality (uk)":
                common + ["amount", "nature", "donor_status"],
            "overseas benefits and gifts":
                common + ["amount", "nature", "donor_status"],
            "remunerated employment, office, profession etc":
                common + ["amount"],
            "remunerated employment, office, profession, etc_":
                common + ["amount"],
            "remunerated employment, office, profession et":
                common + ["amount"],
        }
        results = []
        for category in self.interest_categories:
            interests = []
            category_low = category.lower()

            values = [
                "p.%s" % field for field in category_fields[category_low]
            ]

            search_string = u"""
                MATCH (mp:`Member of Parliament` {{name:"{0}"}}) with mp
                MATCH (mp)-[:INTERESTS_REGISTERED_IN]-(cat) with mp, cat
                    WHERE cat.category = "{1}"
                MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel) with mp, cat, rel
                MATCH (rel)-[:REGISTERED_CONTRIBUTOR]-(int) with mp, cat, rel, int
                MATCH (rel)-[:REMUNERATION_RECEIVED]-(p) with mp, cat, rel, int, p
                RETURN labels(int) as labels, {2}
            """.format(self.vertex["name"], category, ", ".join(values))

            output = self.query(search_string)
            for entry in output:
                interest = {
                    "name": entry["p.contributor"],
                    "labels": entry["labels"]
                }
                if "donor_status" in category_fields[category_low]:
                    interest["donor_status"] = entry["p.donor_status"]
                detail = {
                    "interest": interest,
                    "category": category,
                    "recipient": entry["p.recipient"],
                    "source_url": entry["p.source_url"],
                    "source_fetched": entry["p.source_fetched"],
                    "source_linked_from": entry["p.source_linked_from"],
                    "recorded_date": entry["p.`recorded date`"],
                    "registered": entry["p.registered"],
                }

                if "amount" in category_fields[category_low]:
                    detail["amount"] = self._convert_to_currency(entry["p.amount"])
                    detail["amount_int"] = entry["p.amount"]

                if "visit_dates" in category_fields[category_low]:
                    detail["visit_dates"] = entry["p.visit_dates"]

                if "purpose" in category_fields[category_low]:
                    detail["purpose"] = entry["p.purpose"]

                if "nature" in category_fields[category_low]:
                    detail["nature"] = entry["p.nature"]

                interests.append(detail)

            results.append({"category": category, "interests": interests})

        return results
    
    def _get_interests_summary(self):
        total = self._remuneration_total()
        register = {
            "remuneration_total": self._convert_to_currency(total),
            "remuneration_total_int": total,
            "interest_categories": self._interest_categories_count(),
            "interest_relationships": self._interest_relationships(),
            "remuneration_count": self._remuneration_count(),
        }
        return register

    def _remuneration_total(self):
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}}) WITH mp
            MATCH (mp)-[:INTERESTS_REGISTERED_IN]-(cat) with mp, cat
            MATCH (cat)-[x:INTEREST_RELATIONSHIP]-(rel) with mp, cat, rel
            MATCH (rel)-[y:REMUNERATION_RECEIVED]-(x)
            RETURN sum(x.amount) as total
        """.format(self.vertex["name"])
        return self.query(query)[0]["total"]

    def _interest_categories(self):
        results = []

        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}}) WITH mp
            MATCH (mp)-[:INTERESTS_REGISTERED_IN]-(cat) with mp, cat
            RETURN DISTINCT cat.category
        """.format(self.vertex["name"])
        output = self.query(query)

        # TODO include Clients once parser is fixed
        # TODO include 'Loans and... ' once parsed
        excluded_categories = [
            u"Land and Property",
            u"Clients",
            u"Gifts, benefits and hospitality (UK) Hours: 8 hrs_",
            u"Loans and other controlled transactions",
            u"Remunerated employment, office, profession etc_",
            u"remunerated employment, office, profession et"
        ]

        for entry in output:
            results.append(entry[0])

        for category in excluded_categories:
            if category in results:
                results.remove(category)
                self._logger.debug(" ** excluded category: %s" % category)

        return results

    def _interest_categories_count(self):
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}}) WITH mp
            MATCH (mp)-[:INTERESTS_REGISTERED_IN]-(cat) with mp, cat
            RETURN count(cat) as category_count
        """.format(self.vertex["name"])
        return self.query(query)[0]["category_count"]

    def _interest_relationships(self):
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}}) WITH mp
            MATCH (mp)-[:INTERESTS_REGISTERED_IN]-(cat) with mp, cat
            MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel) with mp, cat, rel
            RETURN count(rel) as relationship_count
        """.format(self.vertex["name"])
        return self.query(query)[0]["relationship_count"]

    def _remuneration_count(self):
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}}) WITH mp
            MATCH (mp)-[:INTERESTS_REGISTERED_IN]-(cat) with mp, cat
            MATCH (cat)-[x:INTEREST_RELATIONSHIP]-(rel) with mp, cat, rel
            MATCH (rel)-[y:REMUNERATION_RECEIVED]-(x)
            RETURN count(x) as remuneration_count
        """.format(self.vertex["name"])
        return self.query(query)[0]["remuneration_count"]

    def _get_donations_summary(self):
        total = self._donation_total()
        ec = {
            "donor_count": self._donor_count(),
            "donation_total": self._convert_to_currency(total),
            "donation_total_int": total
        }
        return ec

    def _donor_count(self):
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}}) WITH mp
            MATCH (mp)-[:FUNDING_RELATIONSHIP]-(rel) with mp, rel
            RETURN DISTINCT count(rel.donor) as donor_count
        """.format(self.vertex["name"])
        return self.query(query)[0]["donor_count"]

    def _donation_total(self):
        query = u"""
            MATCH (mp:`Member of Parliament` {{name: "{0}"}}) WITH mp
            MATCH (mp)-[:FUNDING_RELATIONSHIP]-(rel) with mp, rel
            MATCH (rel)-[y:DONATION_RECEIVED]-(x)
            RETURN sum(x.amount) as total
        """.format(self.vertex["name"])
        return self.query(query)[0]["total"]

    def _get_donations(self):
        results = []
        search_string = u"""
            MATCH (mp:`Member of Parliament` {{name:"{0}"}}) with mp
            MATCH (mp)-[:FUNDING_RELATIONSHIP]-(rel) with mp, rel
            MATCH (rel)-[:DONATION_RECEIVED]-(x) with mp, rel, x
            MATCH (rel)-[:REGISTERED_CONTRIBUTOR]-(p) with mp, rel, p, x
            RETURN p.name, p.donor_type, p.company_reg, x.amount, x.reported_date, x.received_date,
                x.nature, x.purpose, x.ec_reference, x.accepted_date, x.recd_by, labels(p) as labels
            ORDER BY x.received_date DESC
        """.format(self.vertex["name"])
        output = self.query(search_string)
        for entry in output:
            detail = {
                "donor": {
                    "name": entry["p.name"],
                    "donor_type": entry["p.donor_type"],
                    "company_reg": entry["p.company_reg"],
                    "labels": entry["labels"],
                    "details_url": None,
                    "api_url": None
                },
                "amount": self._convert_to_currency(entry["x.amount"]),
                "amount_int": entry["x.amount"],
                "reported": entry["x.reported_date"],
                "received": entry["x.received_date"],
                "accepted": entry["x.accepted_date"],
                "ec_reference": entry["x.ec_reference"],
                "recd_by": entry["x.recd_by"],
                "nature": entry["x.nature"],
                "purpose": entry["x.purpose"]
            }
            results.append(detail)
        return results

    def set_mp_details(self, properties=None):
        properties = self._add_namedentity_properties(properties)
        labels = ["Named Entity", "Member of Parliament"]
        self.set_node_properties(properties, labels)

    def link_position(self, position):
        self.create_relationship(
            self.vertex, "SERVED_IN", position.vertex
        )

    def link_department(self, department):
        self.create_relationship(
            self.vertex, "MEMBER_OF", department.vertex
        )

    def link_interest_category(self, category):
        self.create_relationship(
            self.vertex, "INTERESTS_REGISTERED_IN", category.vertex
        )

    def link_alternate(self, alternate):
        self.create_relationship(
            self.vertex, "ALSO_KNOWN_AS", alternate.vertex
        )

    def link_party(self, name):
        party = PoliticalParty(name)
        party.create()
        if name:
            image = config.mapped_party_images[name]
            properties = {"image_url": image}
        else:
            properties = {"image_url": None}
        party.set_party_details(properties)
        self.create_relationship(
            self.vertex, "MEMBER_OF", party.vertex
        )

    def link_elected_term(self, term):
        self.create_relationship(
            self.vertex, "ELECTED_FOR", term.vertex
        )


class Lords(BaseDataModel):
    def __init__(self):
        BaseDataModel.__init__(self)
        self.count = self._get_lord_count()

    def get_all(self):
        search_string = u"""
            MATCH (lord:`Lord`) with lord
            MATCH (lord)-[r]-() with lord,  r
            RETURN lord.name, lord.party, lord.twfy_id, lord.image,
                count(r) as weight, labels(lord) as labels
            ORDER BY weight DESC
        """
        search_result = self.query(search_string)
        return search_result

    def _get_lord_count(self):
        search_string = u"""
            MATCH (lord:`Lord`)
            RETURN count(lord)
        """
        search_result = self.query(search_string)
        return search_result[0][0]


class Lord(NamedEntity):
    def __init__(self, name=None):
        NamedEntity.__init__(self)
        self.label = "Lord"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            "Named Entity", self.primary_attribute, self.name
        )
        if self.exists:
            self.meetings = self._get_meetings()
            self.meetings_summary = self._get_meetings_summary()
            self.interests = self._get_interests()
            self.interests_summary = self._get_interests_summary()
            self.donations = self._get_donations()
            self.donations_summary = self._get_donations_summary()

    def set_lord_details(self, properties=None):
        properties = self._add_namedentity_properties(properties)
        labels = ["Named Entity", "Lord"]
        self.set_node_properties(properties, labels)

    def link_interest_category(self, category):
        self.create_relationship(
            self.vertex, "INTERESTS_REGISTERED_IN", category.vertex
        )

    def link_party(self, name):
        party = PoliticalParty(name)
        if not party.exists:
            party.create()
        if name:
            image = config.mapped_party_images[name]
            properties = {"image_url": image}
        else:
            properties = {"image_url": None}
        party.set_party_details(properties)
        self.create_relationship(
            self.vertex, "MEMBER_OF", party.vertex
        )

    def link_peerage(self, peerage):
        self.create_relationship(
            self.vertex, "PEERAGE", peerage.vertex
        )

    def link_position(self, position):
        self.create_relationship(self.vertex, "SERVED_IN", position.vertex)

    def _get_meetings_summary(self):
        results = []
        meetings = {"meetings_total": 0}
        query = u"""
            MATCH (lord:`Lord` {{name: "{0}"}}) WITH lord
            MATCH (lord)-[:SERVED_IN]-(p:`Government Office`) with lord, p
            MATCH (p)-[:ATTENDED_BY]-(m) with lord, p, m
                 WHERE m.host_name = "{0}"
            MATCH (m)-[:ATTENDED_BY]-(a:`Meeting Attendee`) with lord, p, m, a
            RETURN p.name, count(a), collect(a.name)
        """.format(self.vertex["name"])
        output = self.query(query)
        for entry in output:
            results.append(
                {
                    "position": entry[0],
                    "meetings_count": entry[1],
                    "influencers_met": list(set(entry[2]))
                }
            )
        meetings["meetings_total"] = sum(m['meetings_count'] for m in results)
        meetings["meetings_per_position"] = results
        return meetings

    def _get_meetings(self):
        results = []
        query = u"""
            MATCH (lord:`Lord` {{name: "{0}"}}) WITH lord
            MATCH (lord)-[:SERVED_IN]-(p:`Government Office`) with lord, p
            MATCH (p)-[:ATTENDED_BY]-(m) with lord, p, m
                WHERE m.host_name = "{0}"
            MATCH (m)-[:ATTENDED_BY]-(a:`Meeting Attendee`) with lord, p, m, a
            RETURN p.name as position, a.name as attendee, m.meeting as meeting,
                m.purpose as purpose, m.date as date
            ORDER BY date
        """.format(self.vertex["name"])
        output = self.query(query)
        for entry in output:
            meeting = {
                "position": entry["position"],
                "attendee": entry["attendee"],
                "purpose": entry["purpose"],
                "meeting": entry["meeting"],
                "date": entry["date"],
            }
            results.append(meeting)
        return results

    def _get_interests(self):
        results = []
        search_string = u"""
            MATCH (lord:`Lord` {{name: "{0}"}}) WITH lord
            MATCH (lord)-[:INTERESTS_REGISTERED_IN]-(cat) with lord, cat
            MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel) with lord, cat, rel
            MATCH (rel)-[:REGISTERED_CONTRIBUTOR]-(int) with lord, cat, rel, int
            RETURN cat.category, rel.position, int.name, int.donor_type,
                int.company_reg, labels(int) as labels
        """.format(self.vertex["name"])
        output = self.query(search_string)
        for entry in output:
            detail = {
                "category": entry["cat.category"],
                "interest": {
                    "name": entry["int.name"],
                    "labels": entry["labels"],
                    "donor_type": entry["int.donor_type"],
                    "company_reg": entry["int.company_reg"],
                    "details_url": None,
                    "api_url": None
                },
                "position": entry["rel.position"]
            }
            results.append(detail)
        return results

    def _get_interests_summary(self):
        register = {
            "interest_relationships": self._interest_relationships(),
            "interest_categories": self._interest_categories()
        }
        return register

    def _interest_categories(self):
        query = u"""
            MATCH (lord:`Lord` {{name: "{0}"}}) WITH lord
            MATCH (lord)-[:INTERESTS_REGISTERED_IN]-(cat) with lord, cat
            RETURN count(cat) as category_count
        """.format(self.vertex["name"])
        return self.query(query)[0]["category_count"]

    def _interest_relationships(self):
        query = u"""
            MATCH (lord:`Lord` {{name: "{0}"}}) WITH lord
            MATCH (lord)-[:INTERESTS_REGISTERED_IN]-(cat) with lord, cat
            MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel) with lord, cat, rel
            RETURN count(rel) as relationship_count
        """.format(self.vertex["name"])
        return self.query(query)[0]["relationship_count"]

    def _get_donations(self):
        results = []
        search_string = u"""
            MATCH (lord:`Lord` {{name: "{0}"}}) WITH lord
            MATCH (lord)-[:REGISTERED_CONTRIBUTOR]-(rel) with rel
            MATCH (rel)-[:DONATION_RECEIVED]-(x) with rel, x
            MATCH (rel)-[:FUNDING_RELATIONSHIP]-(donr) with rel, x, donr
            RETURN donr.name, donr.donee_type, donr.recipient_type,
            x.amount, x.reported_date,x.received_date, x.nature,
            x.purpose,x.accepted_date, x.ec_reference, x.recd_by, labels(donr) as labels
            ORDER by x.reported_date DESC
        """.format(self.vertex["name"])
        output = self.query(search_string)

        for entry in output:
            detail = {
                "recipient": {
                    "name": entry["donr.name"],
                    "labels": entry["labels"],
                    "recipient_type": entry["donr.recipient_type"],
                    "details_url": None,
                    "api_url": None
                },
                "amount_int": entry["x.amount"],
                "amount": self._convert_to_currency(entry["x.amount"]),
                "donee_type": entry["donr.donee_type"],
                "reported": entry["x.reported_date"],
                "received": entry["x.received_date"],
                "accepted": entry["x.accepted_date"],
                "ec_reference": entry["x.ec_reference"],
                "recd_by": entry["x.recd_by"],
                "nature": entry["x.nature"],
                "purpose": entry["x.purpose"]
            }
            results.append(detail)
        return results

    def _get_donations_summary(self):
        total = self._donation_total()
        ec = {
            "donation_count": self._donation_count(),
            "donation_total": self._convert_to_currency(total),
            "donation_total_int": total
        }
        return ec

    def _donation_count(self):
        query = u"""
            MATCH (lord:`Lord` {{name: "{0}"}}) WITH lord
            MATCH (lord)-[x:REGISTERED_CONTRIBUTOR]-() with x
            RETURN count(x) as donation_count
        """.format(self.vertex["name"])
        return self.query(query)[0]["donation_count"]

    def _donation_total(self):
        query = u"""
            MATCH (lord:`Lord` {{name: "{0}"}}) WITH lord
            MATCH (lord)-[:REGISTERED_CONTRIBUTOR]-(rel) with lord, rel
            MATCH (rel)-[:DONATION_RECEIVED]-(x)
            RETURN sum(x.amount) as total
        """.format(self.vertex["name"])
        return self.query(query)[0]["total"]


class PoliticalParties(BaseDataModel):
    def __init__(self):
        BaseDataModel.__init__(self)
        self.count = self._get_count()

    def get_all(self):
        search_string = u"""
            MATCH (d:`Political Party`)
            MATCH (d)-[x]-()
            RETURN d.name, d.image_url, count(x) as weight
            ORDER BY weight DESC
        """
        search_result = self.query(search_string)
        return search_result

    def _get_count(self):
        search_string = u"""
            MATCH (d:`Political Party`)
            RETURN count(d)
        """
        search_result = self.query(search_string)
        return search_result[0][0]


class PoliticalParty(NamedEntity):
    def __init__(self, name):
        NamedEntity.__init__(self)
        self.primary_attribute = "name"
        self.label = "Political Party"
        self.name = name
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.name
        )
        if self.exists:
            self.donations = self._get_donations()
            self.donations_summary = self._get_donations_summary()
            self.mp_count = self._mp_count()
            self.lord_count = self._lord_count()

    def set_party_details(self, properties=None):
        properties = self._add_namedentity_properties(properties)
        labels = ["Named Entity", "Political Party"]
        self.set_node_properties(properties, labels)

    def _mp_count(self):
        query = u"""
            MATCH (p:`Political Party` {{name: "{0}"}})
            MATCH (mp:`Member of Parliament`)-[:MEMBER_OF]-(p)
            RETURN count(mp) as mp_count
        """.format(self.vertex["name"])
        return self.query(query)[0]["mp_count"]

    def _lord_count(self):
        query = u"""
            MATCH (p:`Political Party` {{name: "{0}"}})
            MATCH (l:`Lord`)-[:MEMBER_OF]-(p)
            RETURN count(l) as lord_count
        """.format(self.vertex["name"])
        return self.query(query)[0]["lord_count"]

    def _get_donations(self):
        results = []
        search_string = u"""
            MATCH (p:`Political Party` {{name: "{0}"}})
            MATCH (p)-[:FUNDING_RELATIONSHIP]-(rel) with p, rel
            MATCH (rel)-[:DONATION_RECEIVED]-(x) with p, rel, x
            MATCH (rel)-[:REGISTERED_CONTRIBUTOR]-(d) with p, rel, d, x
            RETURN d.name, d.donor_type, d.company_reg, x.amount, labels(d) as labels,
                x.reported_date, x.received_date, x.accepted_date, x.recd_by, x.ec_reference,
                x.nature, x.purpose
            ORDER BY x.accepted_date DESC
        """.format(self.vertex["name"])
        output = self.query(search_string)
        for entry in output:
            detail = {
                "donor": {
                    "name": entry["d.name"],
                    "labels": entry["labels"],
                    "donor_type": entry["d.donor_type"],
                    "company_reg": entry["d.company_reg"],
                    "details_url": None,
                    "api_url": None
                },
                "amount": self._convert_to_currency(entry["x.amount"]),
                "amount_int": entry["x.amount"],
                "reported": entry["x.reported_date"],
                "received": entry["x.received_date"],
                "accepted": entry["x.accepted_date"],
                "nature": entry["x.nature"],
                "purpose": entry["x.purpose"]
            }
            results.append(detail)
        return results

    def _get_donations_summary(self):
        total, count = self._donations()
        ec = {
            "donation_count": count,
            "donation_total": self._convert_to_currency(total),
            "donation_total_int": total
        }
        return ec

    def _donations(self):
        query = u"""
            MATCH (p:`Political Party` {{name: "{0}"}})
            MATCH (p)-[:FUNDING_RELATIONSHIP]-(x)
            MATCH (x)-[:DONATION_RECEIVED]-(f)
            RETURN p.name as Party, sum(f.amount) as total, count(f.amount) as count
            ORDER BY total DESC
        """.format(self.vertex["name"])
        output = self.query(query)
        if output:
            return output[0]["total"], output[0]["count"]
        else:
            return 0, 0


class GovernmentOffices(BaseDataModel):
    def __init__(self):
        BaseDataModel.__init__(self)
        self.count = self._get_count()

    def get_all(self):
        search_string = u"""
            MATCH (n:`Government Committee`) with n
            MATCH (n)-[:SERVED_IN]-(x) with n, x
                WHERE x.left_reason = "still_in_office"
                    OR x.left_reason = "general_election"
            MATCH (x)-[:ELECTED_FOR]-(p) with n, x, p
            RETURN n.name, labels(n), count(p)
            ORDER BY count(p) DESC
        """
        search_result = self.query(search_string)
        return search_result

    def _get_count(self):
        search_string = u"""
            MATCH (p) where p:Lord OR p:`Member of Parliament` with p
            RETURN count(p)
        """
        search_result = self.query(search_string)
        return search_result[0][0]


class GovernmentOffice(NamedEntity):
    def __init__(self, name=None):
        NamedEntity.__init__(self)
        self.exists = False
        self.label = "Government Office"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.name
        )
        if self.exists:
            self.mp_count = self._mp_count()
            self.members = self._get_members()
            self.interests_summary, self.donation_summary =\
                self._get_office_summary()

    def is_committee(self):
        properties = {"image_url": None}
        labels = ["Named Entity", "Government Committee"]
        self.set_node_properties(properties=properties, labels=labels)

    def is_department(self, office_type="Constituency"):
        properties = {"image_url": None, "office_type": office_type}
        labels = ["Named Entity", "Government Department"]
        self.set_node_properties(properties=properties, labels=labels)

    def is_position(self, office_type="Constituency"):
        properties = {"image_url": None, "office_type": office_type}
        labels = ["Named Entity", "Government Position"]
        self.set_node_properties(properties=properties, labels=labels)

    def link_department(self, department):
        self.create_relationship(
            self.vertex, "OFFICE_IN", department.vertex
        )

    def _mp_count(self):
        query = u"""
            MATCH (n:`Government Office` {{name: "{0}"}}) with n
            MATCH (n)-[:SERVED_IN]-(x) with n, x
                WHERE x.left_reason = "still_in_office"
            MATCH (x)-[:ELECTED_FOR]-(p) with n, x, p
            RETURN count(p) as mp_count
        """.format(self.vertex["name"])
        return self.query(query)[0]["mp_count"]

    def _get_members(self):
        search_string = u"""
            MATCH (n:`Government Office` {{name: "{0}"}}) with n
            MATCH (n)-[:SERVED_IN]-(t) with n, t
                WHERE t.left_reason = "still_in_office"
                    OR t.left_reason = "general_election"
            MATCH (t)-[:ELECTED_FOR]-(p) with n, t, p
            RETURN p.name as name
        """.format(self.vertex["name"])
        result = self.query(search_string)
        return [r["name"] for r in result]

    def _get_office_summary(self):
        results = []
        for name in self.members:
            member = MemberOfParliament(name)
            entry = {
                "ri_total": member.interests_summary["remuneration_total_int"],
                "ri_count": member.interests_summary["remuneration_count"],
                "ri_relationships": member.interests_summary["interest_relationships"],
                "ec_count": member.donations_summary["donor_count"],
                "ec_total": member.donations_summary["donation_total_int"],
            }
            results.append(entry)
        register = {
            "remuneration_count": sum(x['ri_count'] for x in results),
            "interest_relationships": sum(x['ri_relationships'] for x in results),
            "remuneration_total_int": sum(x['ri_total'] for x in results),
            "remuneration_total": self._convert_to_currency(
                sum(x['ri_total'] for x in results)
            )
        }
        donations = {
            "donor_count": sum(x['ec_count'] for x in results),
            "donation_total_int": sum(x['ec_total'] for x in results),
            "donation_total": self._convert_to_currency(
                sum(x['ec_total'] for x in results)
            )
        }
        return register, donations


class GovernmentMeeting(BaseDataModel):
    def __init__(self, term=None):
        BaseDataModel.__init__(self)
        self.exists = False
        self.label = "Government Meeting"
        self.primary_attribute = "meeting"
        self.term = term
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.term
        )

    def create(self):
        self.vertex = self.create_vertex(
            self.label, self.primary_attribute, self.term
        )
        self.exists = True

    def set_meeting_details(self, labels=None, properties=None):
        self.set_node_properties(properties, labels)

    def set_meeting_date(self, date):
        self.set_date(date, "MEETING_HELD")

    def link_participant(self, participant):
        self.create_relationship(self.vertex, "ATTENDED_BY", participant.vertex)


class TermInParliament(BaseDataModel):
    def __init__(self, term=None):
        BaseDataModel.__init__(self)
        self.exists = False
        self.label = "Elected Term"
        self.primary_attribute = "term"
        self.term = term
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.term
        )

    def create(self):
        self.vertex = self.create_vertex(
            self.label, self.primary_attribute, self.term
        )
        self.exists = True

    def link_constituency(self, constituency):
        self.create_relationship(self.vertex, "REPRESENTING", constituency.vertex)

    def set_term_details(self, labels=None, properties=None):
        if properties["entered_house"]:
            self.set_date(properties["entered_house"], "ENTERED_HOUSE")
        if properties["left_reason"]:
            self.set_date(properties["left_house"], "LEFT_HOUSE")
        self.set_node_properties(properties, labels)

    def link_position(self, position):
        self.create_relationship(self.vertex, "SERVED_IN", position.vertex)


class Constituency(BaseDataModel):
    def __init__(self, name=None):
        BaseDataModel.__init__(self)
        self.exists = False
        self.label = "Constituency"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.name
        )

    def create(self):
        self.vertex = self.create_vertex(
            self.label, self.primary_attribute, self.name
        )
        self.exists = True


class DonationRecipient(NamedEntity):
    def __init__(self, name=None):
        NamedEntity.__init__(self)
        self.exists = False
        self.label = "Donation Recipient"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            "Named Entity", self.primary_attribute, self.name
        )

    def set_recipient_details(self, properties=None):
        properties = self._add_namedentity_properties(properties)
        labels = ["Donation Recipient", "Named Entity"]
        self.set_node_properties(properties, labels)

    def link_funding_category(self, category):
        self.create_relationship(
            self.vertex, "FUNDING_RELATIONSHIP", category.vertex
        )