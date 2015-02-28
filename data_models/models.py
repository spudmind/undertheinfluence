# -*- coding: utf-8 -*-
from data_models import core
from utils import config


class NamedEntity(core.BaseDataModel):
    def __init__(self, name=None):
        core.BaseDataModel.__init__(self)
        self.exists = False
        self.label = "Named Entity"
        self.primary_attribute = "name"
        self.name = name

    def create(self):
        self.vertex = self.create_vertex(
            self.label, self.primary_attribute, self.name
        )
        self.exists = True

    @staticmethod
    def _add_namedentity_properties(properties):
        if properties is None:
            properties = {"image_url": None}
        else:
            properties = dict({"image_url": None}, **properties)
        return properties


class MemberOfParliament(NamedEntity):
    def __init__(self, name=None):
        NamedEntity.__init__(self)
        self.label = "Member of Parliament"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.name
        )
        if self.exists:
            self.positions = self._get_positions()
            self.departments = self._get_departments()
            self.interests = self._get_interests()
            self.donations = self._get_donations()

    def _get_positions(self):
        return self._get_government_positions("Government Position")

    def _get_departments(self):
        return self._get_government_positions("Government Department")

    def _get_government_positions(self, pos_type):
        results = []
        search_string = u"""
            MATCH (mp:`Member of Parliament` {{name:"{0}"}}) with mp
            MATCH (mp)-[:ELECTED_FOR]-(const)
            WHERE const.left_reason = "still_in_office" with const
            MATCH (const)-[:SERVED_IN]-(p:`Government Position`) with p.name AS position
            RETURN position
        """.format(self.vertex["name"], pos_type)
        output = self.query(search_string)
        for entry in output:
            results.append(entry[0])
        return results

    def _get_interests(self):
        results = []
        search_string = u"""
            MATCH (mp:`Member of Parliament` {{name:"{0}"}}) with mp
            MATCH (mp)-[:INTERESTS_REGISTERED_IN]-(cat) with mp, cat
            MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel) with mp, cat, rel
            MATCH (rel)-[:REGISTERED_CONTRIBUTOR]-(int) with mp, cat, rel, int
            MATCH (rel)-[:REMUNERATION_RECEIVED]-(p) with mp, cat, rel, int, p
            RETURN cat.category, int.name, int.donor_type, int.company_reg,
                p.amount, p.received, p.registered, labels(int) as labels
            ORDER BY p.received DESC
        """.format(self.vertex["name"])
        output = self.query(search_string)
        for entry in output:
            detail = {
                "interest": {
                    "name": entry["int.name"],
                    "labels": entry["labels"],
                    "donor_type": entry["int.donor_type"],
                    "company_reg": entry["int.company_reg"],
                    "details_url": None,
                    "api_url": None
                },
                "category": entry["cat.category"],
                "amount_int": entry["p.amount"],
                "amount": _convert_to_currency(entry["p.amount"]),
                "received": entry["p.received"],
                "registered": entry["p.registered"]
            }
            results.append(detail)
        return results

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
                "amount": _convert_to_currency(entry["x.amount"]),
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
            self.vertex, "IN_POSITION", position.vertex
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


class MembersOfParliament(core.BaseDataModel):
    def __init__(self):
        core.BaseDataModel.__init__(self)
        self.count = self._get_mp_count()

    def get_all(self):
        search_string = u"""
            MATCH (mp:`Member of Parliament`) with mp
            MATCH (mp)-[r]-() with mp,  r
            RETURN mp.name, mp.party, mp.twfy_id, mp.guardian_image as image_ul,
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


class Lord(NamedEntity):
    def __init__(self, name=None):
        NamedEntity.__init__(self)
        self.label = "Lord"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.name
        )
        if self.exists:
            self.interests = self._get_interests()
            self.donations = self._get_donations()

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
                "amount": _convert_to_currency(entry["x.amount"]),
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


class Lords(core.BaseDataModel):
    def __init__(self):
        core.BaseDataModel.__init__(self)
        self.count = self._get_lord_count()

    def get_all(self):
        search_string = u"""
            MATCH (lord:`Lord`) with lord
            MATCH (lord)-[r]-() with lord,  r
            RETURN lord.name, lord.party, lord.twfy_id,
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


class Donor(NamedEntity):
    def __init__(self, name=None):
        NamedEntity.__init__(self)
        self.exists = False
        self.label = "Donor"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            "Named Entity", self.primary_attribute, self.name
        )

    def set_donor_details(self, properties=None):
        properties = self._add_namedentity_properties(properties)
        labels = ["Donor", "Named Entity"]
        self.set_node_properties(properties, labels)


class FundingRelationship(core.BaseDataModel):
    def __init__(self, relationship=None):
        core.BaseDataModel.__init__(self)
        self.exists = False
        self.label = "Funding Relationship"
        self.primary_attribute = "relationship"
        self.relationship = relationship
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.relationship
        )

    def create(self):
        self.vertex = self.create_vertex(
            self.label, self.primary_attribute, self.relationship
        )
        self.exists = True

    def set_category_details(self, properties=None):
        self.set_node_properties(properties)

    def update_raw_record(self, raw_record):
        existing = self.vertex["raw_record"]
        if existing and len(existing) > 0:
            new = u"{}\n---\n\n{}".format(existing, raw_record)
        else:
            new = raw_record
        self.vertex["raw_record"] = new
        self.vertex.push()

    def link_donor(self, donor):
        self.create_relationship(
            self.vertex, "REGISTERED_CONTRIBUTOR", donor.vertex
        )

    def link_funding(self, funding):
        self.create_relationship(
            self.vertex, "DONATION_RECEIVED", funding.vertex
        )

    def link_payment(self, payment):
        self.create_relationship(
            self.vertex, "REMUNERATION_RECEIVED", payment.vertex
        )

    def set_registered_date(self, date):
        self.set_date(date, "REGISTERED")


class InterestCategory(core.BaseDataModel):
    def __init__(self, name=None):
        core.BaseDataModel.__init__(self)
        self.exists = False
        self.label = "Interest Category"
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

    def update_category_details(self, properties=None):
        self.set_node_properties(properties)

    def link_relationship(self, relationship):
        self.create_relationship(
            self.vertex, "INTEREST_RELATIONSHIP", relationship.vertex
        )


class RegisteredInterest(NamedEntity):
    def __init__(self, name=None):
        NamedEntity.__init__(self)
        self.exists = False
        self.label = "Registered Interest"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            "Named Entity", self.primary_attribute, self.name
        )

    def set_interest_details(self, properties=None):
        properties = self._add_namedentity_properties(properties)
        labels = ["Named Entity", "Registered Interest"]
        self.set_node_properties(properties, labels)


class Influencer(core.BaseDataModel):
    def __init__(self, name):
        core.BaseDataModel.__init__(self)
        self.primary_attribute = "name"
        self.label = "Named Entity"
        self.name = name
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.name
        )
        if self.exists:
            self.interests = self._get_interests()
            self.donations = self._get_donations()

    def _get_interests(self):
        results = []
        search_string = u"""
            MATCH (n:`Named Entity` {{name: "{0}"}}) WITH n
            MATCH (n)-[:REGISTERED_CONTRIBUTOR]-(rel)
            MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel)
            MATCH (p)-[:INTERESTS_REGISTERED_IN]-(cat)
            OPTIONAL MATCH (rel)-[:REMUNERATION_RECEIVED]-(x)
            RETURN p.name, p.party, cat.category, x.amount,
                labels(p) as labels
            ORDER by x.reported_date DESC
        """.format(self.vertex["name"])
        output = self.query(search_string)
        for entry in output:
            detail = {
                "interest": {
                    "name": entry["p.name"],
                    "party": entry["p.party"],
                    "labels": entry["labels"],
                    "details_url": None,
                    "api_url": None
                },
                "category": entry["cat.category"],
                "amount": _convert_to_currency(entry["x.amount"]),
                "amount_int": entry["x.amount"]
            }
            results.append(detail)
        return results

    def _get_donations(self):
        results = []
        search_string = u"""
            MATCH (n:`Named Entity` {{name: "{0}"}}) WITH n
            MATCH (n)-[:REGISTERED_CONTRIBUTOR]-(rel) with rel
            MATCH (rel)-[:DONATION_RECEIVED]-(x) with rel, x
            MATCH (rel)-[:FUNDING_RELATIONSHIP]-(donr) with rel, x, donr
            RETURN donr.name, donr.donee_type, donr.recipient_type,
            x.amount, x.reported_date,x.received_date, x.nature,
            x.purpose, x.accepted_date, x.ec_reference,x.recd_by, labels(donr) as labels
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
                "amount": _convert_to_currency(entry["x.amount"]),
                "amount_int": entry["x.amount"],
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


class Influencers(core.BaseDataModel):
    def __init__(self):
        core.BaseDataModel.__init__(self)
        self.count = self._get_count()

    def get_all(self):
        search_string = u"""
            MATCH (inf) where inf:Donor OR inf:`Registered Interest` with inf
            MATCH (inf)<-[y:REGISTERED_CONTRIBUTOR|FUNDING_RELATIONSHIP]-(x)
            RETURN DISTINCT inf.name as influencer, inf.donor_type, labels(inf), count(y) as weight
            ORDER BY weight DESC
        """
        search_result = self.query(search_string)
        return search_result

    def _get_count(self):
        search_string = u"""
            MATCH (inf) WHERE inf:Donor OR inf:`Registered Interest`
            RETURN count(inf)
        """
        search_result = self.query(search_string)
        return search_result[0][0]


class RegisteredDonation(core.BaseDataModel):
    def __init__(self, donation=None):
        core.BaseDataModel.__init__(self)
        self.exists = False
        self.label = "Donation"
        self.primary_attribute = "donation"
        self.donation = donation
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.donation
        )

    def create(self):
        self.vertex = self.create_vertex(
            self.label, self.primary_attribute, self.donation
        )
        self.exists = True

    def set_donations_details(self, properties=None):
        labels = ["Donation", "Contributions"]
        self.set_node_properties(properties, labels)

    def set_dates(self, received, reported, accepted):
        if received and len(received) > 0:
            self._set_received_date(received)
        if reported and len(reported) > 0:
            self._set_reported_date(reported)
        if accepted and len(accepted) > 0:
            self._set_accepted_date(accepted)

    def _set_received_date(self, date):
        self.set_date(date, "RECEIVED")

    def _set_reported_date(self, date):
        self.set_date(date, "REPORTED")

    def _set_accepted_date(self, date):
        self.set_date(date, "ACCEPTED")


class Remuneration(core.BaseDataModel):
    def __init__(self, summary=None):
        core.BaseDataModel.__init__(self)
        self.exists = False
        self.label = "Remuneration"
        self.primary_attribute = "summary"
        self.summary = summary
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.summary
        )

    def create(self):
        self.vertex = self.create_vertex(
            self.label,
            self.primary_attribute,
            self.summary,
            merge=True
        )
        self.exists = True

    def set_remuneration_details(self, properties=None):
        labels = ["Remuneration", "Contributions"]
        self.set_node_properties(properties, labels)

    def set_registered_date(self, date):
        self.set_date(date, "REGISTERED")

    def set_received_date(self, date):
        self.set_date(date, "RECEIVED")


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

    def set_party_details(self, properties=None):
        properties = self._add_namedentity_properties(properties)
        labels = ["Named Entity", "Political Party"]
        self.set_node_properties(properties, labels)

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
                "amount": _convert_to_currency(entry["x.amount"]),
                "amount_int": entry["x.amount"],
                "reported": entry["x.reported_date"],
                "received": entry["x.received_date"],
                "accepted": entry["x.accepted_date"],
                "nature": entry["x.nature"],
                "purpose": entry["x.purpose"]
            }
            results.append(detail)
        return results


class PoliticalParties(core.BaseDataModel):
    def __init__(self):
        core.BaseDataModel.__init__(self)
        self.count = self._get_count()

    def get_all(self):
        search_string = u"""
            MATCH (d:`Political Party`)
            MATCH (d)-[x]-()
            RETURN d.name, count(x) as weight
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

    def is_department(self):
        properties = {"image_url": None}
        labels = ["Named Entity", "Government Department"]
        self.set_node_properties(properties=properties, labels=labels)

    def is_position(self):
        properties = {"image_url": None}
        labels = ["Named Entity", "Government Position"]
        self.set_node_properties(properties=properties, labels=labels)


class TermInParliament(core.BaseDataModel):
    def __init__(self, term=None):
        core.BaseDataModel.__init__(self)
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


class Constituency(core.BaseDataModel):
    def __init__(self, name=None):
        core.BaseDataModel.__init__(self)
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


def _convert_to_currency(number):
    if isinstance(number, int):
        return u'£{:20,.2f}'.format(number)
    else:
        return None
