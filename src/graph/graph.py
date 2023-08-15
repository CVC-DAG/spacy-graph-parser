import networkx as nx

from src.vis.visutils import plot_graph_from_nx

class Node:
    """
    Class representing a node in the graph.

    Attributes:
        id (str): Unique identifier for the node.
        text (str): Text content of the node.
        ner_category (str): Named Entity Recognition category of the node.
        pos_tag (str): Part of speech tag of the node.
        attributes (dict): Dictionary of miscellaneous attributes associated with the node.
    """

    def __init__(self, id, text, ner_category, pos_tag, attributes=None):
        """
        Initialize a Node object.

        Args:
            id (str): Unique identifier for the node.
            text (str): Text content of the node.
            ner_category (str): Named Entity Recognition category of the node.
            pos_tag (str): Part of speech tag of the node.
            attributes (dict, optional): Dictionary of miscellaneous attributes. Defaults to None.
        """
        self.id = id
        self.text = text
        self.ner_category = ner_category
        self.pos_tag = pos_tag
        self.attributes = attributes or {}

    def __str__(self):
        return f"Node(ID: {self.id}, Text: '{self.text}', NER: {self.ner_category}, POS: {self.pos_tag})"


class Edge:
    """
    Class representing an edge in the graph.

    Attributes:
        source_id (str): ID of the source node.
        target_id (str): ID of the target node.
        label (str): Label describing the relationship between source and target nodes.
    """

    def __init__(self, source_id, target_id, label):
        """
        Initialize an Edge object.

        Args:
            source_id (str): ID of the source node.
            target_id (str): ID of the target node.
            label (str): Label describing the relationship between source and target nodes.
        """
        self.source_id = source_id
        self.target_id = target_id
        self.label = label

    def __str__(self):
        return f"Edge(Source: {self.source_id}, Target: {self.target_id}, Label: '{self.label}')"


class Graph:
    """
    Class representing a graph with nodes and edges.

    Attributes:
        nodes (dict): Dictionary to store nodes with their IDs as keys.
        edges (list): List to store edge objects in the graph.
    """

    def __init__(self):
        """
        Initialize a Graph object.
        """
        self.nodes = {}
        self.edges = []

    def add_node(self, node):
        """
        Add a node to the graph.

        Args:
            node (Node): Node object to be added to the graph.
        """
        self.nodes[node.id] = node

    def add_edge(self, edge, force = False):
        """
        Add an edge to the graph.

        Args:
            edge (Edge): Edge object to be added to the graph.
        """
        if not force:
            for used_edge in self.edges:
                if sorted([edge.source_id, edge.target_id]) == sorted([used_edge.source_id, used_edge.target_id]):
                    return None # Don't duplicate edges
        self.edges.append(edge)
    
    def get_nodes_by(self, query, by='text'):
        
        """
        Get nodes based on a given attribute and query.

        Args:
            query (str): Query value to match against the specified attribute.
            by (str): Attribute to search by (e.g., 'text', 'ner_category', 'pos_tag', etc.).

        Returns:
            list: List of nodes that match the query for the specified attribute.
        """
        matching_nodes = []

        for node in self.nodes.values():
            attribute_value = getattr(node, by, None)
            if attribute_value is not None and query in attribute_value:
                matching_nodes.append(node)

        return matching_nodes
    
    def to_nx_graph(self):
        nx_graph = nx.DiGraph()
        for node in self.nodes:
            node_instance = self.nodes[node]

            nx_graph.add_node(node, **vars(node_instance))
        
        for edge in self.edges:
            nx_graph.add_edge(edge.source_id, edge.target_id, label = edge.label)
            
        return nx_graph
    
    def plot(self):
        plot_graph_from_nx(self.to_nx_graph())

    def __str__(self):
        graph_str = "Graph:\n"
        
        for edge in self.edges:
            source_node = self.nodes.get(edge.source_id)
            target_node = self.nodes.get(edge.target_id)
            
            if source_node and target_node:
                graph_str += f"{source_node.text} <--{edge.label}--> {target_node.text}\n"
        
        return graph_str
    
    

