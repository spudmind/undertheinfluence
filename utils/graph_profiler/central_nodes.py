from utils.graph_profiler import DataProfiler


class CentralNodes(DataProfiler):
    def __init__(self):
        DataProfiler.__init__(self)
        self.node_types = [
            ("Named Entity", "name"),
            ("Member of Parliament", "name"),
            ("Contributor", "name"),
            ("Government Department", "name"),
            ("Government Position", "name"),
            ("Political Party", "name"),
            ("Interest Category", "name"),
            ("Registered Interest", "summary"),
            ("Remuneration", "summary")
        ]
        self.outgoing = ["outgoing", "-", "->"]
        self.incoming = ["incoming", "<-", "-"]
        print "[**] Highly Connected Nodes\n"

    def show_nodes(self):
        for node_type in self.node_types:
            print node_type[0]
            self._get_node_centrality(node_type, *self.outgoing)
            self._get_node_centrality(node_type, *self.incoming)
            print "\n"
        #for node_type in self.node_types:
        #    self._get_node_centrality(node_type, *self.incoming)

    def _get_node_centrality(self, node, direction, left, right):
        print " Top %s relationships" % direction
        search_string = u"""
                MATCH (n:`{0}`) {1}[rel]{2} ()
                RETURN n.{3}, type(rel) as rel_type, count(rel) as degree
                ORDER BY degree DESC
                LIMIT 5
            """.format(node[0], left, right, node[1])
        output = self.core_model.query(search_string)
        for result in output:
            result_node, relationship, count = result[0], result[1], result[2]
            self._print_count(direction, relationship, count, result_node)

    @staticmethod
    def _print_count(direction, relationship, count, node):
        output = " %-20s%-25s%-10s" % (count, relationship, node)
        print output.encode('utf-8')
