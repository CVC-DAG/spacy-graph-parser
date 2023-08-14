import spacy
from src.nlp.parsing import SpacyTextParser

QUERY = 'Orden aprobando las oposiciones celebradas para proveer 25 Auxiliares de Dibujo líneal\
    y nombrando Auxiliares numerarios de Dibujo lineal de las Escuelas de Artes y Oficios Artísticos que se citan a los señores que se mencionan.\
    Confiriendo, promoviendo y nombrando á los sujetos que se expresan. Fallecimiento en Oporto del Excmo. Sr. D. Francisco de Taranco y Llano.\
    Esta persona corre una carrera.\
    Petersburgo, 7 de febrero de 1808.- \
    De los 180 regimientos que había reunido el general Buxhoeden de orden del Emperador en Lituania, sólo quedan 30 en esta provincia, mientras los demás van caminando hacia las fronteras de Turquía y las de Suecia.'
    
if __name__ == '__main__':

    # NER FOR QUERY #
    model = spacy.load('es_core_news_sm')
    parser = SpacyTextParser(model = model)
    parser.parse_sentence(QUERY)

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
    parser.graph.plot()

else: raise AssertionError('Just your luck! Unitary tests should never be imported.')