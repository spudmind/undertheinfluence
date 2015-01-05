from data_models import core


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

    def _get_positions(self):
        return self._get_government_positions("Government Position")

    def _get_departments(self):
        return self._get_government_positions("Government Department")

    def _get_government_positions(self, pos_type):
        search_string = u"""
            MATCH (mp:`Member of Parliament` {{name:"{0}"}}) with mp
            MATCH (mp)-[:REPRESENTATIVE_FOR]-(const)
            WHERE const.left_reason = "still_in_office" with const
            MATCH (const)-[:SERVED_IN]-(p:`{1}`) with COLLECT(p.name) AS positions
            RETURN positions
        """.format(self.vertex["name"], pos_type)
        output = self.query(search_string)
        return output[0][0]

    def update_mp_details(self, properties=None):
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

    def link_party(self, party):
        party = NamedEntity(party)
        party_labels = ["Political Party"]
        if not party.exists:
            party.create()
        party.set_node_properties(labels=party_labels)
        self.create_relationship(
            self.vertex, "MEMBER_OF", party.vertex
        )

    def link_elected_term(self, term):
        self.create_relationship(
            self.vertex, "ELECTED_FOR", term.vertex
        )


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
        labels = ["Government Department"]
        self.set_node_properties(labels=labels)

    def is_position(self):
        labels = ["Government Position"]
        self.set_node_properties(labels=labels)


class InterestCategory(NamedEntity):
    def __init__(self, name=None):
        NamedEntity.__init__(self)
        self.exists = False
        self.label = "Interest Category"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.name
        )

    def link_interest(self, interest):
        self.create_relationship(
            self.vertex, "REGISTERED_INTEREST", interest.vertex
        )


class RegisteredInterest(NamedEntity):
    def __init__(self, name=None):
        NamedEntity.__init__(self)
        self.exists = False
        self.label = "Registered Interest"
        self.primary_attribute = "name"
        self.name = name
        self.exists = self.fetch(
            self.label, self.primary_attribute, self.name
        )

    def update_interest_details(self, properties=None):
        self.set_node_properties(properties)


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

    def update_details(self, properties=None):
        if properties["entered_house"]:
            self.set_date(properties["entered_house"], "ENTERED_HOUSE")
        if properties["left_reason"]:
            self.set_date(properties["left_house"], "LEFT_HOUSE")

    def link_position(self, position):
        self.create_relationship(self.vertex, "SERVED_IN", position.vertex)