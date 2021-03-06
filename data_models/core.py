# -*- coding: utf-8 -*-
from data_interfaces import graph_database
import logging
import calendar
import re


class BaseDataModel:
    def __init__(self):
        self.g = graph_database.GraphInterface()
        self._logger = logging.getLogger('spud')
        self.vertex = None
        self.label = None
        self.document_label = 'Document'
        self.named_label = "Named Entity"
        self.category_fields = self._set_categories()

    def fetch(self, label, primary_attribute, search):
        exists = False
        self.vertex = self.find_vertex(
            label, primary_attribute, search
        )
        if self.vertex:
            exists = True
        return exists

    def find_vertex(self, label, node_key, value):
        search_query = u"""
                MATCH (v:`{0}` {{{1}:"{2}"}})
                RETURN v
            """.format(label, node_key, value)
        output = self.query(search_query)
        if output:
            return output[0][0]
        else:
            return None

    def find_entity(self, name):
        results = []
        search_query = u"""
                MATCH (entity:`Named Entity` {{name: "{0}"}})
                RETURN entity.name, labels(entity)
            """.format(name)
        output = self.query(search_query)
        if output:
            for entry in output:
                detail = {
                    "name": entry[0],
                    "labels": entry[1]
                }
                results.append(detail)
        return results

    def create_vertex(self, label, node_key, value, merge=True):
        self.vertex = None
        if merge:
            search_query = u"""
                    MERGE (v:`{0}` {{{1}:"{2}"}})
                    ON MATCH set v:`{0}`
                    ON CREATE set v:`{0}`
                    RETURN v
                """.format(label, node_key, value)
        else:
            search_query = u"""
                    CREATE (v:`{0}` {{{1}:"{2}"}})
                    RETURN v
                """.format(label, node_key, value)
            #print search_query
        output = self.query(search_query)
        self.vertex = output[0][0]
        self.vertex.labels.add(label)
        return self.vertex

    def set_node_properties(self, properties=None, labels=None):
        if properties:
            node_properties = self.vertex.pull()
            for prop in properties:
                self.vertex.properties[prop] = properties[prop]
        if labels:
            if isinstance(labels, list):
                for label in labels:
                    self.vertex.labels.add(label)
            else:
                self.vertex.labels.add(labels)
        self.vertex.push()

    def create_relationship(self, vertex1, relationship, vertex2):
        rel_query = u"""
            START n=node({0}), m=node({1})
            MERGE (n)-[r:{2}]-(m)
            RETURN r
        """.format(vertex1._id, vertex2._id, relationship)
        return self.query(rel_query)

    def query(self, query_string):
        return self.g.graph.cypher.execute(query_string)

    def get_all_nodes(self, node_type):
        search_string = u"MATCH (n:`{0}`) RETURN n".format(node_type)
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def _set_categories(self):
        common = [
            "contributor",
            "amount",
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
            "miscellaneous": common,
            "miscellaneous and unremunerated interests": common,
            "remunerated employment, office, profession etc": common,
            "remunerated employment, office, profession, etc_": common,
            "remunerated employment, office, profession et": common,
            "overseas visits": common + ["visit_dates", "purpose"],
            "sponsorships": common + ["donor_status"],
            "sponsorship or financial or material support": common + ["donor_status"],
            "gifts, benefits and hospitality (uk)":
                common + ["donor_status", "nature", ],
            "overseas benefits and gifts":
                common + ["donor_status", "nature"],

        }
        return category_fields

    def set_date(self, date, relationship):
        converted = self._convert_date(date)
        if converted:
            self.create_relationship(
                self.vertex,
                relationship,
                self.g.calendar.date(converted[0], converted[1], converted[2]).day
            )

    def _convert_date(self, date):
        year_month_day = None
        try:
            if '/' in date:
                d = date.split('/')
                month, day, year = int(d[0]), int(d[1]), int(d[2])
            elif '-' in date:
                d = date.split('-')
                year, month, day = int(d[0]), int(d[1]), int(d[2])
            elif ' ' in date:
                d = date.split(' ')
                month_digit = self._convert_month(d[1])
                day, month, year = int(d[0]), int(month_digit), int(d[2])
            year_month_day = (year, month, day)
            return year_month_day
        except:
            return year_month_day

    @staticmethod
    def _convert_to_currency(number):
        if isinstance(number, int):
            return u'£{:20,}'.format(number)
        else:
            return None

    def named_entity_export(self):
        search_query = u"""
                MATCH (n:`Named Entity`)
                RETURN n.name, labels(n)
            """
        output = self.query(search_query)
        if output:
            for result in output:
                try:
                    #self._logger.debug("%s\t%s" % (result[0], result[1]))
                    print "%s\t%s" % (result[0], result[1])
                except UnicodeEncodeError:
                    pass

    @staticmethod
    def _format_content(string):
        old_content = string.split("\n\n")
        new_content = ""
        for para in old_content:
            new_content += u"<p>{0}</p>".format(para)
        return new_content

    @staticmethod
    def _date_to_dictionary(date):
        date = date.split(" ")
        if re.search('\d+', date[0]):
            day = date[0]
            month = date[1]
            year = date[2]
        else:
            day = date[1]
            month = date[2]
            year = date[3]
        #print day, month, year
        d = dict((v, k) for k, v in enumerate(calendar.month_abbr))
        return {"day": int(day), "month": d[month], "year": int(year)}

    @staticmethod
    def _convert_month(text):
        month_to = {v: k for k, v in enumerate(calendar.month_abbr)}
        return month_to[text[:3]]


class NamedEntity(BaseDataModel):
    def __init__(self, name=None):
        BaseDataModel.__init__(self)
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
            return {"image_url": None}
        else:
            if not "image_url" in properties:
                properties["image_url"] = None
            return properties