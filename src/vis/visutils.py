import networkx as nx
import matplotlib.pyplot as plt


def plot_graph_from_nx(graph, attr='text', where='tp.png', figsize=(32, 32), prune=True):
    if prune:
        graph = preprocess_graph(graph)
        
    plt.figure(1, figsize=figsize) 
    pos = nx.planar_layout(graph)
    colors = {tag: idx for idx, tag in enumerate(set([tag for _, tag in graph.nodes(data = 'pos_tag')]))}
    assigned_colors = [colors[tag] for _, tag in graph.nodes(data = 'pos_tag')]
    
    
    nx.draw(graph, pos, node_color = assigned_colors, labels=nx.get_node_attributes(graph, attr))
    nx.draw_networkx_edge_labels(graph, pos, edge_labels={(a, b): label for a, b, label in graph.edges(data='label')})
    
    if isinstance(where, str):
        plt.savefig(where)
        plt.clf()

    else:
        plt.show()



def preprocess_graph(graph):
    # First, remove nodes with "< CET >" as text attribute
    nodes_to_remove = [node for node, data in graph.nodes(data=True) if data.get('text') == '< CET >']
    graph.remove_nodes_from(nodes_to_remove)
    
    # Second, remove nodes with degree 0
    nodes_to_remove = [node for node, degree in dict(graph.degree()).items() if degree == 0]
    graph.remove_nodes_from(nodes_to_remove)
    
    return graph
