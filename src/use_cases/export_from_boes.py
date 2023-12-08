import spacy
from src.nlp.parsing import SpacyTextParser
import networkx as nx
import os
import json
from neo4j import GraphDatabase
from getpass import getpass
import uuid
from tqdm import tqdm


def receive_args():
    import argparse
    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description='Process JSONs root and model tag')

    # Adding arguments
    parser.add_argument('--jsons_root', default='/data2/users/amolina/BOE_original/BOEv2/', type=str,
                        help='Root directory for JSON files')
    parser.add_argument('--model_tag', default='es_dep_news_trf', help='Tag for the model')
    parser.add_argument('--neo4j_uri', default='bolt://158.109.9.181:7687', help='Connection for Neo4J Database')
    parser.add_argument('--neo4j_user', default='neo4j', help='Connection for Neo4J Database')

    # Parse the arguments
    return parser.parse_args()


def list_all_json_files(directory):
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('_gt.json'):
                json_files.append(os.path.join(root, file))
    return json_files


def post_process_gexf(gexf):
    pass


def create_or_get_ocr_token_node(node_data, session):
    word = node_data['text']

    query = (
        "OPTIONAL MATCH (n:OCRToken {text: $word}) "
        "RETURN ID(n) AS node_id"
    )

    result = session.run(query, {'word': word.lower()})
    existing_node = result.single()

    if existing_node and existing_node['node_id'] is not None:
        return existing_node['node_id']
    else:
        create_query = (
            "CREATE (n:OCRToken {text: $word, original_word: $ocr_org}) "
            "RETURN ID(n) AS node_id"
        )
        create_result = session.run(create_query, {'word': word.lower(), 'ocr_org': word})
        new_node = create_result.single()
        return new_node['node_id'] if new_node else None


def main():
    args = receive_args()
    model = spacy.load(args.model_tag)

    parser = SpacyTextParser(model=model, position_sensitive=True)
    passwd = 'xG2Lak4drDR'  # getpass() #TODO ELIMINATE THIS BEFORE COMMIT
    driver = GraphDatabase.driver(args.neo4j_uri, auth=(args.neo4j_user, passwd))
    session = driver.session(database='neo4j')
    print(session)

    query_link_doc_to_layout = (
        "MATCH (d:Document) WHERE d.uuid_4 = $document_uuid "
        "WITH d "
        "UNWIND $layout_components AS lc "
        "CREATE (d)-[:CONTAINS]->(:LayoutComponent {"
        "    _pk: lc.primary_key, "
        "    page_of_document: lc.page_of_document, "
        "    uuid_4: lc.uuid_4, "
        "    raw_ocr: lc.raw_ocr, "
        "    bbox: lc.bbox, "
        "    type: lc.type"
        "})"
    )

    for num, file in enumerate(list_all_json_files(args.jsons_root)):

        document_data = json.load(open(
            file, 'r'
        ))
        document_properties = {
            'id': document_data['file'].replace('.pdf', ''),
            'year': document_data['date'].split('/')[-1],
            'date': document_data['date'],
            'era': file.split('/')[-3],
            'num_pages': len(document_data['pages']),
            'uuid_4': document_data['file'].replace('.pdf', ''),
            'document_href': document_data['document_href']
        }

        _ = session.run(
            "CREATE (a:Document) "
            "SET a = $document_properties "
            "RETURN a", document_properties=document_properties
        )
        result = session.run(
            "MATCH (a {uuid_4: $uuid_value}) "
            "MERGE (y:Year {year: $year_value}) "
            "MERGE (a)-[:PUBLISHED_IN]->(y) "
            "RETURN y",
            {'uuid_value': document_data['file'].replace('.pdf', ''), 'year_value': document_properties['year']}
        )

        for page in document_data['pages']:
            for idx, layout_component in enumerate(document_data['pages'][page]):
                pk = f"{document_properties['uuid_4']}_{page}_{idx}"
                layout_component_properties = {
                    'page_of_document': page,
                    'uuid_4': str(uuid.uuid4()),
                    'raw_ocr': layout_component['ocr'],
                    'bbox': layout_component['bbox'],
                    'type': layout_component['type'],
                    'primary_key': pk
                }

                session.run(query_link_doc_to_layout, document_uuid=document_properties['uuid_4'],
                            layout_components=layout_component_properties)

                parser.parse_sentence(layout_component_properties['raw_ocr'], override=True)
                # parser.parse_quantities()
                parser.parse_attribute_to_subject()
                parser.ner_tagger()
                parser.parse_verbs_to_subject()

                graph = parser.graph.to_nx_graph()
                print(f"Layout component {idx} from page {page} of document {num}")

                for node, data in graph.nodes(data=True):

                    result = create_or_get_ocr_token_node(data, session)
                    assert result is not None, 'No keyword was updated'

                    query = (
                        'MATCH (region) WHERE region.uuid_4={} '
                        'MATCH (node) WHERE node.text={} '
                        'MERGE (region)-[r:CONTAINS_KEYWORD]->(node) '
                        'SET r = $func_properties '
                        'RETURN region, node'
                    )
                    result = session.run(
                        query.format(f"'{document_properties['uuid_4']}'", f"'{data['text'].lower()}'"),
                        pk_region=pk, node_text_identifier=data['text'].lower(),
                        func_properties={'pos_tag': data['pos_tag'],
                                         'NER': data['ner_category'] if len(data['ner_category']) else None}
                    )


if __name__ == '__main__':
    main()
