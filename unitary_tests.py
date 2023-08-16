import spacy
from spacy import displacy
from src.nlp.parsing import SpacyTextParser
import networkx as nx

QUERY = '\n'.join(open('media/single.txt', 'r').readlines())
    
if __name__ == '__main__':

    # NER FOR QUERY #
    model = spacy.load('es_dep_news_trf')
    parser = SpacyTextParser(model = model, position_sensitive = True)
    parser.parse_sentence(QUERY)
    print(QUERY)

    try:
        parser.ner_tagger()
        
    except Exception as e:
        print(f"NER is not working, reason: {e}")
        
    try:
        parser.parse_verbs_to_subject()
        
    except Exception as e:
        print(f"subj / Verb / Obj is not working, reason: {e}")
        
    try:
        parser.parse_attribute_to_subject()
        
    except Exception as e:
        print(f"sATTRs is not working, reason: {e}")
    
    try:
        parser.parse_quantities()
        
    except Exception as e:
        print(f"Quantities is not working, reason: {e}")
        
    try:
        parser.parse_chunks_and_cd()
        
    except Exception as e:
        print(f"Quantities is not working, reason: {e}")
        
        
    try:
        parser.parse_preps()
        
    except Exception as e:
        print(f"Prepositions is not working, reason: {e}")
    parser.graph.plot()
    nxgraph = parser.graph.to_nx_graph()
    nx.write_gexf(nxgraph, 'tmp.gexf')
    
    # displacy.serve(parser.sntc,)

else: raise AssertionError('Just your luck! Unitary tests should never be imported.')