from utils.graph_profiler import DataProfiler


class NodeCount(DataProfiler):
    def __init__(self):
        DataProfiler.__init__(self)
        print "[**] Node Counts\n"

    def show_counts(self):
        self._get_total()
        self._get_relationships()
        print "-"
        for node_type in self.node_types:
            self._print_count(node_type, self._get_count(node_type))
        print "---"

    def _get_total(self):
        search_string = "MATCH (n) RETURN count(n) as count"
        result = self.core_model.query(search_string)
        self._print_count("TOTAL NODES", result[0][0])

    def _get_relationships(self):
        search_string = "MATCH ()-[n]-() RETURN count(n) as count"
        result = self.core_model.query(search_string)
        self._print_count("TOTAL RELATIONSHIPS", result[0][0])

    def _get_count(self, node_type):
        search_string = "MATCH (n:`%s`) RETURN count(n) as count" % node_type
        result = self.core_model.query(search_string)
        return result[0][0]

    @staticmethod
    def _print_count(label, count):
        print "%-25s%-5s" % (label, count)
