from time import strftime
from utils.graph_profiler import node_summary as nodes
from utils.graph_profiler import network_centrality
from utils.graph_profiler import central_nodes


current_time = strftime("%Y-%m-%d %H:%M:%S")
print "\nData Profile"
print current_time
print "---"


def get_profile():
    node_count = nodes.NodeCount()
    node_count.show_counts()
    structure = network_centrality.InOutDegree()
    structure.show_degrees()
    centre = central_nodes.CentralNodes()
    centre.show_nodes()

get_profile()

