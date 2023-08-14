import networkx as nx
import matplotlib.pyplot as plt

def plot_graph_from_nx(graph, attr = 'text', where = 'tp.png', figsize = (32, 32)):
    plt.figure(1,figsize=(figsize)) 
    nx.draw(graph, labels = nx.get_node_attributes(graph, attr), )
    if isinstance(where, str): plt.savefig(where)
    else: plt.show()