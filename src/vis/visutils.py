import networkx as nx
import matplotlib.pyplot as plt

def plot_graph_from_nx(graph, attr = 'text', where = 'tp.png', figsize = (32, 32)):
    plt.figure(1,figsize=(figsize)) 
    pos = nx.fruchterman_reingold_layout(graph)
    nx.draw(graph, pos, labels = nx.get_node_attributes(graph, attr), )
    nx.draw_networkx_edge_labels(graph, pos, edge_labels={(a,b): label for a, b, label in graph.edges(data='label')})
    if isinstance(where, str): plt.savefig(where)
    else: plt.show()