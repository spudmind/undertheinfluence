from utils.graph_profiler import DataProfiler


class InOutDegree(DataProfiler):
    def __init__(self):
        DataProfiler.__init__(self)
        self.outgoing = ["outgoing", "-", "->"]
        self.incoming = ["incoming", "<-", "-"]
        print "\n[**] Centrality / Relationship Counts\n"

    def show_degrees(self):
        for node_type in self.node_types:
            print node_type
            self._get_connection_degrees(node_type, *self.outgoing)
            self._get_connection_degrees(node_type, *self.incoming)
            print "---\n"
        #print "Node Type inDegree"
        #for node_type in self.node_types:
        #    self._get_connection_degrees(node_type, *self.incoming)

    def _get_connection_degrees(self, node_type, direction, left, right):
        search_string = """
                        MATCH (n:`{0}`) {1}[rel]{2} ()
                        RETURN type(rel) as rel_type, count(rel) as degree
                        ORDER BY degree DESC
                        """.format(node_type, left, right)
        output = self.core_model.query(search_string)
        for result in output:
            self._print_count(direction, result[0], result[1])

    def _print_count(self, direction, rel_type, count):
        output = " %-25s%-10s%-10s" % (rel_type, count, direction)
        print output.encode('utf-8')

