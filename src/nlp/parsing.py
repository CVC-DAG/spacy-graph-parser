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
    quantity_edge = 'has_quantity'
    in_context = 'in_context'
    is_object = 'has_object'
    
    entity = '<ENT>'
    
    def __init__(self, model = 'es_core_news_sm', sentence = None, position_sensitive = False) -> None:
        self.nlp_model = spacy.load(model) if isinstance(model, str) else model # passig the model itself as efficiency measure
        self.sntc = None # don't parse it twice!
        self.graph = Graph()
        self.position_sensitive = position_sensitive
        if sentence is not None: self.parse_sentence(sentence)
        
        self.node_unique_ids = -1 # Keep Control On graph IDs
        # TODO: It should be controlled from Graph cass but whatever
    
    def parse_sentence(self, sentence, override = False):
        if self.sntc is not None and not override: raise AssertionError('Trying to override a parsed sentence, use override = True if it was intentional.') 
        self.sntc = self.nlp_model(sentence)

    def _get_new_id(self):
        self.node_unique_ids = self.node_unique_ids + 1
        return self.node_unique_ids
    
    def get_node_in_graph(self, token):
        nodes = self.graph.get_nodes_by(token.text, by = 'text')
        matches = [node for node in nodes if (node.attributes['spacy_token'].i == token.i and self.position_sensitive) or (node.text.lower() == token.text.lower() and not self.position_sensitive)]
        if len(matches):
            assert len(matches) == 1, f'Duplicated node, {token.text}'
            return matches[0]
        
        return None
        
    def construct_node_after_check(self, token):
        node_in_graph = self.get_node_in_graph(token)
        if node_in_graph is None: node_in_graph = Node(self._get_new_id(), token.text, token.ent_type_, token.pos_, {'spacy_token': token, 'bio': token.ent_iob_, 'position': token.i, 'type': 'word'})
        return node_in_graph

    def create_connection(self, token_1, token_2, label):
        
        node_1 = self.construct_node_after_check(token_1)
        node_2 = self.construct_node_after_check(token_2)
        
        self.graph.add_node(node_1)
        self.graph.add_node(node_2)
        
        edge = Edge(node_1.id, node_2.id, label=label)
        self.graph.add_edge(edge)
        
        return node_1, node_2, edge

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
        for token in self.sntc:
            if "subj" in token.dep_:
                subject = token
                verb = token.head
                obj = [child for child in token.head.children if "obj" in child.dep_]
                if obj: self.create_connection(subject, obj[0], verb.text)
       
    def parse_attribute_to_subject(self):
        '''
        Here we will find attributes to stablish SUBJ --- IS ---> ATTR chains
        
        '''
        for token in self.sntc:
            
            if token.dep_ in ["amod", "attr"]:

                adjective = token
                noun = token.head               
                self.create_connection(noun, adjective, self.has_attr)
    
    def parse_chunks_and_cd(self):
        '''
        Here we will be parsing the chunks in the graph for COMPLEMENT DIRECTE relations: https://spacy.io/usage/linguistic-features#noun-chunks
        
        
        '''

        return None
    
    
    def parse_quantities(self):
        for token in self.sntc:
            if token.pos_ == "NUM":
                quantity = token
                quantity_object = token.head
                self.create_connection(quantity_object, quantity, self.quantity_edge)            
                for obj in list(quantity_object.children):
                    if obj.dep_ == 'obj': self.create_connection(quantity_object, obj,self.in_context )