import spacy 

from src.graph.graph import Node, Edge, Graph
    
def find_deepest_children(token_childrens, previous_token, chain = {}):
    for token in token_childrens:
        chain[previous_token] = token
        find_deepest_children(token.children, token, chain)
    return chain
    
    

class SpacyTextParser:
    
    belongs_to_ner = 'belongs_to_ner'
    has_attr = 'has_attr'
    
    entity = '<ENT>'
    
    def __init__(self, model = 'es_core_news_sm', sentence = None) -> None:
        self.nlp_model = spacy.load(model) if isinstance(model, str) else model # passig the model itself as efficiency measure
        self.sntc = None # don't parse it twice!
        self.graph = Graph()
        if sentence is not None: self.parse_sentence(sentence)
        
        self.node_unique_ids = -1 # Keep Control On graph IDs
        # TODO: It should be controlled from Graph cass but whatever
    
    def parse_sentence(self, sentence, override = False):
        if self.sntc is not None and not override: raise AssertionError('Trying to override a parsed sentence, use override = True if it was intentional.') 
        self.sntc = self.nlp_model(sentence)

    def _get_new_id(self):
        self.node_unique_ids = self.node_unique_ids + 1
        return self.node_unique_ids

    def ner_tagger(self):
        '''
        
        Here we will find the different named entities and consider them as cliques
        
        '''
        
        if self.sntc is None: raise AttributeError('Please, parse a sentence using .parse_sentence(whatever: str)')
        ner_attrs = [{'text': e.text, 'ner_category': e.ent_type_, 'ner_bio': e.ent_iob_, 'token': e} for e in self.sntc if len(e.ent_type_)]
        
        ner_groups = {}
        for idx, ner in enumerate(ner_attrs):
            if ner['ner_bio'] == 'B': group_id = len(ner_groups) + 1
            if not group_id in ner_groups: ner_groups[group_id] = list()
            ner_groups[group_id].append(ner)
        
        for group in ner_groups.values():
            category = list(set([ner['ner_category'] for ner in group]))
            assert len(category) == 1, 'Multiple categories for a single NER group found.'
            
            node_group_id = self._get_new_id()
            ner_main_node = Node(node_group_id, f"<{category[0]}>", category[0], None, {'type': f'{self.entity}'})
            self.graph.add_node(ner_main_node)
            
            for named_entity in group:
                ner_node = self.construct_node_after_check(named_entity['token'])
                relation = Edge(ner_node.id, node_group_id, self.belongs_to_ner)

                self.graph.add_node(ner_node)
                self.graph.add_edge(relation)
            
    
    def parse_verbs_to_subject(self):
        '''
        Here we will find verbs to stablish SUBJ --- verb ---> OBJ chains
        
        '''
        pass
        
    def get_node_in_graph(self, token):
        nodes = self.graph.get_nodes_by(token.text, by = 'text')
        matches = [node for node in nodes if node.attributes['spacy_token'].i == token.i]
        if len(matches):
            assert len(matches) == 1, f'Duplicated node, {token.text}'
            return matches[0]
        
        return None
        
    def construct_node_after_check(self, token):
        node_in_graph = self.get_node_in_graph(token)
        if node_in_graph is None: node_in_graph = Node(self._get_new_id(), token.text, token.ent_type_, token.pos_, {'spacy_token': token, 'bio': token.ent_iob_, 'position': token.i, 'type': 'word'})
        return node_in_graph

    def parse_attribute_to_subject(self):
        '''
        Here we will find attributes to stablish SUBJ --- IS ---> ATTR chains
        
        '''
        for token in self.sntc:
            
            if token.dep_ == "amod":
                
                adjective = token
                noun = token.head
                
                adj_node = self.construct_node_after_check(adjective)
                noun_node = self.construct_node_after_check(noun)
                
                self.graph.add_node(adj_node)
                self.graph.add_node(noun_node)
                
                edge = Edge(noun_node.id, adj_node.id, label=self.has_attr)
                self.graph.add_edge(edge)
    
    def parse_chunks_and_cd(self):
        '''
        Here we will be parsing the chunks in the graph for COMPLEMENT DIRECTE relations: https://spacy.io/usage/linguistic-features#noun-chunks
        
        
        '''
        for chunk in self.sntc.noun_chunks:
            root_token = chunk.root
            head_token = root_token.head
            dependency_label = root_token.dep_
            
            print(f"Root: {root_token.text}, Head: {head_token.text}, Relationship: {dependency_label}")
        
    def parse_quantities(self):
        for token in self.sntc:
            if token.pos_ == "NUM":
                quantity = token
                quantity_object = token.head
                if quantity_object:
                    quantity_node = self.construct_node_after_check(quantity)
                    quantity_object_node = self.construct_node_after_check(quantity_object)
                    
                    label = self.has_attr if quantity_object.head is None else quantity_object.head.text
                    self.graph.add_node(quantity_node)
                    self.graph.add_node(quantity_object_node)
                    self.graph.add_edge(Edge(quantity_object_node.id, quantity_node.id, label=label))
            
            