
from datetime import datetime
from data_models.core import NamedEntity, BaseDataModel


class Influencer(BaseDataModel):
    def __init__(self, name):
        BaseDataModel.__init__(self)
        self.primary_attribute = "name"
        self.label = "Named Entity"
        self.name = name
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.name
        )
        if self.exists:
            self.interests = self._get_interests()
            self.donations = self._get_donations()
            self.lobbyists = self._get_lobbyists()
            self.meetings = self._get_meetings()
            self.meetings_summary = self._get_meetings_summary()
            self.interests_summary = self._get_interests_summary()
            self.donations_summary = self._get_donations_summary()
            self.lobbyists_summary = self._get_lobbyists_summary()

    def _get_lobbyists(self):
        results = []
        search_string = u"""
            MATCH (n:`Named Entity` {{name: "{0}"}}) WITH n
            MATCH (n)-[:HIRED]-(rel) with n, rel
            MATCH (rel)-[:REGISTERED_LOBBYIST]-(lob) with n, rel, lob
            RETURN lob.name, rel.from_date, rel.to_date,
                lob.contact_details, lob.address
        """.format(self.name)
        output = self.query(search_string)
        for entry in output:
            detail = {
                "name": entry["lob.name"],
                "from": entry["rel.from_date"],
                "to": entry["rel.to_date"],
                "contact_details": entry["lob.contact_details"],
            }
            results.append(detail)
        return results

    def _get_lobbyists_summary(self):
        search_string = u"""
            MATCH (n:`Named Entity` {{name: "{0}"}}) WITH n
            MATCH (n)-[:HIRED]-(rel) with n, rel
            MATCH (rel)-[:REGISTERED_LOBBYIST]-(lob) with n, rel, lob
            RETURN count(lob) as total
        """.format(self.name)
        count = self.query(search_string)[0]["total"]
        return {"lobbyist_hired": count}

    def _get_meetings_summary(self):
        return {
            "meetings_count": self._meetings_total_count(),
            "politician_count": len(set(self._politicians_met())),
            "department_count": len(set(self._departments_met())),
            "politicians_met": self._politicians_met(),
            "departments_met": self._departments_met()
        }

    def _meetings_total_count(self):
        query = u"""
            MATCH (a:`Named Entity` {{name: "{0}"}})
            MATCH (m)-[:ATTENDED_BY]-(a) with m, a
            MATCH (m)-[:ATTENDED_BY]-(g:`Government Office`) with a, m, g
            OPTIONAL MATCH (mp)-[:SERVED_IN]-(g) with a, m, g, mp
            RETURN count(m) as total
        """.format(self.vertex["name"])
        return self.query(query)[0]["total"]

    def _politicians_met(self):
        results = []
        query = u"""
            MATCH (a:`Named Entity` {{name: "{0}"}})
            MATCH (m)-[:ATTENDED_BY]-(a) with m, a
            MATCH (m)-[:ATTENDED_BY]-(g:`Government Office`) with a, m, g
            OPTIONAL MATCH (mp)-[:SERVED_IN]-(g) with a, m, g, mp
            RETURN DISTINCT  mp.name as host
        """.format(self.vertex["name"])
        output = self.query(query)
        for entry in output:
            if entry[0]:
                results.append(entry[0])
        return results

    def _departments_met(self):
        results = []
        query = u"""
            MATCH (a:`Named Entity` {{name: "{0}"}})
            MATCH (m)-[:ATTENDED_BY]-(a) with m, a
            MATCH (m)-[:ATTENDED_BY]-(g:`Government Office`) with a, m, g
            OPTIONAL MATCH (mp)-[:SERVED_IN]-(g) with a, m, g, mp
            RETURN DISTINCT  m.department
        """.format(self.vertex["name"])
        output = self.query(query)
        for entry in output:
            if entry[0]:
                results.append(entry[0])
        return results

    def _get_meetings(self):
        results = []
        query = u"""
            MATCH (a:`Meeting Attendee` {{name: "{0}"}})
            MATCH (m)-[:ATTENDED_BY]-(a) with m, a
            MATCH (m)-[:ATTENDED_BY]-(g:`Government Office`) with a, m, g
            MATCH (mp)-[:SERVED_IN]-(g) with a, m, g, mp
            RETURN g.name as position, mp.name as host, mp.party as party,
                m.meeting as meeting, m.title as title, m.purpose as purpose,
                m.date as date, m.source_url, m.source_linked_from, m.source_fetched
        """.format(self.vertex["name"])
        output = self.query(query)
        for entry in output:
            title = entry["title"]
            if not title:
                title = entry["meeting"].split(" - ")[0]
            meeting = {
                "position": entry["position"],
                "host": entry["host"],
                "party": entry["party"],
                "title": entry["title"],
                "purpose": entry["purpose"],
                "meeting": entry["meeting"],
                "date": entry["date"],
                "source_url": entry["m.source_url"],
                "source_fetched": entry["m.source_fetched"],
                "source_linked_from": entry["m.source_linked_from"],
            }
            results.append(meeting)
        return results

    def _get_interests(self):
        results = []
        search_string = u"""
            MATCH (n:`Named Entity` {{name: "{0}"}}) WITH n
            MATCH (n)-[:REGISTERED_CONTRIBUTOR]-(rel)
            MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel)
            MATCH (p)-[:INTERESTS_REGISTERED_IN]-(cat)
            MATCH (rel)-[:REMUNERATION_RECEIVED]-(x)
                WHERE x.contributor = "{0}"
            RETURN p.name, p.party, cat.category, x.amount, x.source_url, x.registered,
            labels(p) as labels
            ORDER by x.registered DESC
        """.format(self.name)
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
                "amount": self._convert_to_currency(entry["x.amount"]),
                "amount_int": entry["x.amount"],
                "source_url": entry["x.source_url"],
                "registered": entry["x.registered"],
            }
            results.append(detail)
        return results

    def _get_interests_summary(self):
        total = self._remuneration_total()
        register = {
            "relationship_count": self._interest_relationships(),
            "remuneration_total": self._convert_to_currency(total),
            "remuneration_total_int": total,
            "remuneration_count": self._remuneration_count()
        }
        return register

    def _interest_relationships(self):
        query = u"""
            MATCH (inf:`Named Entity` {{name: "{0}"}})
            MATCH (inf)-[:REGISTERED_CONTRIBUTOR]-(rel)
            MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel)
            RETURN count(rel) as count
        """.format(self.name)
        return self.query(query)[0]["count"]

    def _remuneration_total(self):
        query = u"""
            MATCH (inf:`Named Entity` {{name: "{0}"}})
            MATCH (inf)-[:REGISTERED_CONTRIBUTOR]-(rel)
            MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel)
            MATCH (rel)-[:REMUNERATION_RECEIVED]-(x)
            RETURN sum(x.amount) as total
        """.format(self.name)
        return self.query(query)[0]["total"]

    def _remuneration_count(self):
        query = u"""
            MATCH (inf:`Named Entity` {{name: "{0}"}})
            MATCH (inf)-[:REGISTERED_CONTRIBUTOR]-(rel)
            MATCH (cat)-[:INTEREST_RELATIONSHIP]-(rel)
            MATCH (rel)-[:REMUNERATION_RECEIVED]-(x)
            RETURN count(x) as count
        """.format(self.name)
        return self.query(query)[0]["count"]

    def _get_donations(self):
        results = []
        search_string = u"""
            MATCH (n:`Named Entity` {{name: "{0}"}}) WITH n
            MATCH (n)-[:REGISTERED_CONTRIBUTOR]-(rel) with rel
            MATCH (rel)-[:DONATION_RECEIVED]-(x) with rel, x
            MATCH (rel)-[:FUNDING_RELATIONSHIP]-(donr) with rel, x, donr
            RETURN donr.name, donr.donee_type, donr.recipient_type,
            x.amount, x.reported_date,x.received_date, x.nature,
            x.purpose, x.accepted_date, x.ec_reference, x.recd_by, labels(donr) as labels
            ORDER by x.reported_date DESC
        """.format(self.name)
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
                "amount": self._convert_to_currency(entry["x.amount"]),
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

    def _get_donations_summary(self):
        total = self._donation_total()
        ec = {
            "donation_count": self._donation_count(),
            "donation_total": self._convert_to_currency(total),
            "donation_total_int": total
        }
        return ec

    def _donation_total(self):
        query = u"""
            MATCH (inf:`Named Entity` {{name: "{0}"}})
            MATCH (inf)-[:REGISTERED_CONTRIBUTOR]-(rel)
            MATCH (rel)-[:DONATION_RECEIVED]-(x)
            RETURN sum(x.amount) as total
        """.format(self.name)
        return self.query(query)[0]["total"]

    def _donation_count(self):
        query = u"""
            MATCH (inf:`Named Entity` {{name: "{0}"}})
            MATCH (inf)-[:REGISTERED_CONTRIBUTOR]-(rel)
            MATCH (rel)-[:DONATION_RECEIVED]-(x)
            RETURN count(x) as count
        """.format(self.name)
        return self.query(query)[0]["count"]


class Influencers(BaseDataModel):
    def __init__(self):
        BaseDataModel.__init__(self)
        self.count = self._get_count()

    def get_all(self):
        search_string = u"""
            MATCH (inf) WHERE inf:Donor OR inf:`Registered Interest` OR inf:`Meeting Attendee`
                OR inf:`LobbyAgency Client` OR inf:`Lobby Agency Client` with inf
            MATCH (inf)<-[y:REGISTERED_CONTRIBUTOR|FUNDING_RELATIONSHIP|HIRED|ATTENDED_BY]-(x)
            RETURN DISTINCT inf.name as influencer, inf.donor_type, labels(inf), count(y) as weight
            ORDER BY weight DESC
        """
        search_result = self.query(search_string)
        return search_result

    def get_top(self, count):
        pass

    def _get_count(self):
        search_string = u"""
            MATCH (inf) WHERE inf:Donor OR inf:`Registered Interest` OR inf:`Meeting Attendee`
                OR inf:`LobbyAgency Client` OR inf:`Lobby Agency Client` with inf
            RETURN count(inf)
        """
        search_result = self.query(search_string)
        return search_result[0][0]


class LobbyAgency(NamedEntity):
    def __init__(self, name=None):
        NamedEntity.__init__(self)
        self.exists = False
        self.label = "Lobby Agency"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            "Named Entity", self.primary_attribute, self.name
        )
        if self.exists:
            self.contact_details = self._get_contact_details()
            self.clients = self._get_clients()
            self.employees = self._get_employees()
            count = self._get_counts()
            self.client_count = count[0]
            self.employee_count = count[1]
            self.meetings = self._get_meetings()
            self.meetings_summary = self._get_meetings_summary()

    def set_lobbyist_details(self, properties=None):
        properties = self._add_namedentity_properties(properties)
        labels = ["Lobby Agency", "Named Entity"]
        self.set_node_properties(properties, labels)

    def _get_contact_details(self):
        query = u"""
            MATCH (f:`Lobby Agency` {{name: "{0}"}})
            RETURN f.contact_details
        """.format(self.name)
        return self.query(query)[0][0]

    def _get_clients(self):
        results = []
        search_string = u"""
            MATCH (f:`Lobby Agency` {{name: "{0}"}})
            MATCH (f)-[:REGISTERED_LOBBYIST]-(r) with f, r
            MATCH (r)-[:HIRED]-(c) with f, r, c
            MATCH (c)-[x]-() with f, r, c, x
            RETURN c.name as name, labels(c) as labels,
                count(x) as weight, r.to_date, r.from_date
                ORDER BY weight DESC
        """.format(self.name)
        output = self.query(search_string)
        for entry in output:
            detail = {
                "name": entry["name"],
                "weight": entry["weight"],
                "to_date": entry["r.to_date"],
                "from_date": entry["r.from_date"],
                "labels": entry["labels"],
                "source_url": None,
                "source_linked_from": None
            }
            results.append(detail)
        return results

    def _get_employees(self):
        results = []
        search_string = u"""
            MATCH (f:`Lobby Agency` {{name: "{0}"}})
            MATCH (f)-[:REGISTERED_LOBBYIST]-(r) with f, r
            MATCH (r)-[:WORKS_FOR]-(e) with f, r, e
            RETURN e.name as name, labels(e) as labels,
                r.to_date, r.from_date
        """.format(self.name)
        output = self.query(search_string)
        for entry in output:
            detail = {
                "name": entry["name"],
                "to_date": entry["r.to_date"],
                "from_date": entry["r.from_date"],
                "labels": entry["labels"],
                "source_url": None,
                "source_linked_from": None
            }
            results.append(detail)
        return results

    def _get_counts(self):
        search_string = u"""
            MATCH (f:`Lobby Agency` {{name: "{0}"}})
            MATCH (f)-[:REGISTERED_LOBBYIST]-(r) with f, r
            OPTIONAL MATCH (r)-[:HIRED]-(c) with f, r, c
            OPTIONAL MATCH (r)-[:WORKS_FOR]-(e) with f, r, c, e
            RETURN count(c) as clients, count(e) as employees
        """.format(self.name)
        output = self.query(search_string)
        return output[0]["clients"], output[0]["employees"]

    def _get_meetings_summary(self):
        return {
            "meeting_count": self._meetings_total_count(),
            "politician_count": len(self._politicians_met()),
            "department_count": len(self._departments_met()),
            "politicians_met": self._politicians_met(),
            "departments_met": self._departments_met()
        }

    def _meetings_total_count(self):
        query = u"""
            MATCH (f:`Lobby Agency` {{name: "{0}"}})
            MATCH (m)-[:ATTENDED_BY]-(f) with m, f
            RETURN count(m) as total
        """.format(self.vertex["name"])
        return self.query(query)[0]["total"]

    def _politicians_met(self):
        results = []
        query = u"""
            MATCH (f:`Lobby Agency` {{name: "{0}"}})
            MATCH (m)-[:ATTENDED_BY]-(f) with m, f
            MATCH (m)-[:ATTENDED_BY]-(g:`Government Office`) with f, m, g
                OPTIONAL MATCH (mp)-[:SERVED_IN]-(g) with f, m, g, mp
                    WHERE mp.name = m.host_name
            RETURN DISTINCT mp.name as mp
        """.format(self.vertex["name"])
        output = self.query(query)
        for entry in output:
            if entry[0]:
                results.append(entry[0])
        return results

    def _departments_met(self):
        results = []
        query = u"""
            MATCH (f:`Lobby Agency` {{name: "{0}"}})
            MATCH (m)-[:ATTENDED_BY]-(f) with m, f
            MATCH (m)-[:ATTENDED_BY]-(g:`Government Office`) with f, m, g
            RETURN DISTINCT g.name
        """.format(self.vertex["name"])
        output = self.query(query)
        for entry in output:
            if entry[0]:
                results.append(entry[0])
        return results

    def _get_meetings(self):
        results = []
        query = u"""
            MATCH (f:`Lobby Agency` {{name: "{0}"}})
            MATCH (m)-[:ATTENDED_BY]-(f) with m, f
            MATCH (m)-[:ATTENDED_BY]-(g:`Government Office`) with f, m, g
                OPTIONAL MATCH (mp)-[:SERVED_IN]-(g) with f, m, g, mp
                    WHERE mp.name = m.host_name
            RETURN g.name as position, mp.name as host, m.meeting as meeting,
                m.purpose as purpose, m.date as date
        """.format(self.vertex["name"])
        output = self.query(query)
        for entry in output:
            meeting = {
                "position": entry["position"],
                "host": entry["host"],
                "purpose": entry["purpose"],
                "meeting": entry["meeting"],
                "date": entry["date"],
            }
            results.append(meeting)
        return results


class LobbyAgencies(BaseDataModel):
    def __init__(self):
        BaseDataModel.__init__(self)
        self.count = self._get_count()

    def get_all(self):
        search_string = u"""
            MATCH (f:`Lobby Agency`)
            MATCH (f)-[:REGISTERED_LOBBYIST]-(r) with f, r
            OPTIONAL MATCH (r)-[:HIRED]-(c) with f, r, c
            OPTIONAL MATCH (r)-[:WORKS_FOR]-(e) with f, r, c, e
            RETURN f.name, count(c) as clients, count(e) as employees, labels(f)
            ORDER BY clients DESC
        """
        search_result = self.query(search_string)
        return search_result

    def _get_count(self):
        search_string = u"""
            MATCH (f:`Lobby Agency`)
            RETURN count(f)
        """
        search_result = self.query(search_string)
        return search_result[0][0]


class LobbyEmployee(NamedEntity):
    def __init__(self, name=None):
        NamedEntity.__init__(self)
        self.exists = False
        self.label = "Lobby Employee"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            "Named Entity", self.primary_attribute, self.name
        )

    def set_employee_details(self, properties=None):
        properties = self._add_namedentity_properties(properties)
        labels = ["Lobby Employee", "Named Entity"]
        self.set_node_properties(properties, labels)


class LobbyingClient(NamedEntity):
    def __init__(self, name=None):
        NamedEntity.__init__(self)
        self.exists = False
        self.label = "Lobby Agency Client"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            "Named Entity", self.primary_attribute, self.name
        )

    def set_client_details(self, properties=None):
        properties = self._add_namedentity_properties(properties)
        labels = ["Lobby Agency Client", "Named Entity"]
        self.set_node_properties(properties, labels)


class LobbyRelationship(BaseDataModel):
    def __init__(self, relationship=None):
        BaseDataModel.__init__(self)
        self.exists = False
        self.label = "Lobby Relationship"
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

    def set_relationship_details(self, properties=None):
        self.set_node_properties(properties)

    def update_raw_record(self, raw_record):
        existing = self.vertex["raw_record"]
        if existing and len(existing) > 0:
            new = u"{}\n---\n\n{}".format(existing, raw_record)
        else:
            new = raw_record
        self.vertex["raw_record"] = new
        self.vertex.push()

    def link_firm(self, firm):
        self.create_relationship(
            self.vertex, "REGISTERED_LOBBYIST", firm.vertex
        )

    def link_staff(self, staff):
        self.create_relationship(
            self.vertex, "WORKS_FOR", staff.vertex
        )

    def link_client(self, client):
        self.create_relationship(
            self.vertex, "HIRED", client.vertex
        )

    def set_from_date(self, new_date):
        new_datetime = self._make_datetime(new_date)
        existing = self.vertex["from_date"]
        if existing and len(existing) > 0:
            existing_datetime = self._make_datetime(existing)
            if new_datetime < existing_datetime:
                self.vertex["from_date"] = new_date
        else:
            self.vertex["from_date"] = new_date
        self.vertex.push()

    def set_to_date(self, new_date):
        new_datetime = self._make_datetime(new_date)
        existing = self.vertex["to_date"]
        if existing and len(existing) > 0:
            existing_datetime = self._make_datetime(existing)
            if new_datetime > existing_datetime:
                self.vertex["to_date"] = new_date
        else:
            self.vertex["to_date"] = new_date
        self.vertex.push()

    @staticmethod
    def _make_datetime(date):
        if "-" in date:
            t = date.split("-")
            return datetime(int(t[0]), int(t[1]), int(t[2]))


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


class FundingRelationship(BaseDataModel):
    def __init__(self, relationship=None):
        BaseDataModel.__init__(self)
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

    def set_relationship_details(self, properties=None):
        self.set_node_properties(properties)

    def update_raw_record(self, raw_record):
        existing = self.vertex["raw_record"]
        if existing and len(existing) > 0:
            new = u"{}\n,\n{}".format(existing, raw_record)
        else:
            new = raw_record
        self.vertex["raw_record"] = new
        self.vertex.push()

    def link_contributor(self, donor):
        self.create_relationship(
            self.vertex, "REGISTERED_CONTRIBUTOR", donor.vertex
        )

    def link_funding(self, funding):
        self.create_relationship(
            self.vertex, "DONATION_RECEIVED", funding.vertex
        )

    def link_interest_detail(self, payment):
        self.create_relationship(
            self.vertex, "REMUNERATION_RECEIVED", payment.vertex
        )

    def set_registered_date(self, date):
        self.set_node_properties({"registered": date})
        self.set_date(date, "REGISTERED")

    def set_received_date(self, date):
        self.set_node_properties({"received": date})
        self.set_date(date, "REGISTERED")


class MeetingAttendee(NamedEntity):
    def __init__(self, name=None):
        NamedEntity.__init__(self)
        self.exists = False
        self.label = "Meeting Attendee"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            "Named Entity", self.primary_attribute, self.name
        )

    def set_attendee_details(self, properties=None):
        properties = self._add_namedentity_properties(properties)
        labels = ["Named Entity", "Meeting Attendee"]
        self.set_node_properties(properties, labels)


class InterestCategory(BaseDataModel):
    def __init__(self, name=None):
        BaseDataModel.__init__(self)
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


class RegisteredDonation(BaseDataModel):
    def __init__(self, donation=None):
        BaseDataModel.__init__(self)
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


class InterestDetail(BaseDataModel):
    def __init__(self, summary=None):
        BaseDataModel.__init__(self)
        self.exists = False
        self.label = "Interest Detail"
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

    def update_recorded_dates(self, date):
        existing = self.vertex["recorded date"]
        if existing and len(existing) > 0 and not date == existing:
            new = u"{},{}".format(existing, date)
        else:
            new = date
        self.vertex["recorded date"] = new
        self.vertex.push()

    def update_raw_record(self, raw_record):
        existing = self.vertex["raw_record"]
        if existing and len(existing) > 0:
            new = u"{}\n---\n\n{}".format(existing, raw_record)
        else:
            new = raw_record
        self.vertex["raw_record"] = new
        self.vertex.push()

    def set_interest_details(self, properties=None):
        labels = ["Interest Detail", "Contributions"]
        self.set_node_properties(properties, labels)

    def set_registered_date(self, date):
        self.set_date(date, "REGISTERED")

    def set_received_date(self, date):
        self.set_date(date, "RECEIVED")