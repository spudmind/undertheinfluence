from py2neo import Graph, neo4j, rel, node
from py2neo.ext.calendar import GregorianCalendar


class GraphInterface:
    def __init__(self):
        self.URI = 'http://localhost:7474/db/data/'
        self.neo4j = neo4j
        self.rel = rel
        self.graph = Graph(self.URI)
        self.node = node
        self.calendar = GregorianCalendar(self.graph)
        self.relationship = neo4j.Relationship
        #print '\nneo4j connection established\n', self.graph



