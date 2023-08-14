import spacy
from src.nlp.parsing import SpacyTextParser

QUERY = 'Anuncio del Tribunal que ha de juzgar el concurso-oposición convocado para la provisión de la cátedra de "Economía, \
    Organización y Legislación" vacante en la Escuela Técnica Superior de Ingenieros Industriales de Bilbao, por el que se señala lugar,\
    día y hora para la presentación de los opositores admitidos.\
    Decreto 2319/1959, de 24 de diciembre, por el que se declara la urgencia de la ocupación de los terrenos afectados por las obras de prolongación de mina y captación de aguas con destino al Municipio de Mellid (La Coruña).\
    Real orden recordando a los funcionarios de Hacienda de todas las categorías la prohibición legal de ser Agentes o Representantes de toda persona, entidad o\
    Corporación que tuviera asuntos pendientes en las oficinas centrales o provinciales de la Hacienda pública; y dando prevenciones para la tramitación de expedientes y\
    despacho de asuntos, para las operaciones de ingreso y pagos, y para señalar horas para recibir al público y Agentes de Negocios.'
    
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