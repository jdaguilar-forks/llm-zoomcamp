import os

from typing import Dict, List, Union
from elasticsearch import Elasticsearch, exceptions

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


def search(*args, **kwargs) -> List[Dict]:
    """
    query_embedding: Union[List[int], np.ndarray]
    """
    
    connection_string = kwargs.get('connection_string', 'http://elastic_host:9200')
    print(connection_string)
    index_name = kwargs.get('index_name', 'documents')
    print(index_name)
    top_k = kwargs.get('top_k', 5)
    chunk_column = kwargs.get('chunk_column', 'content')
    question = kwargs.get('question', 'content')

    
    search_query = {
        "size": top_k,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": question,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields"
                    }
                }
            }
        },
        "_source": [chunk_column]
    }

    print("Sending script query:", search_query)

    es_client = Elasticsearch(connection_string)
    
    try:

        response = es_client.search(index=index_name, body=search_query)
        print("Raw response from Elasticsearch:", response)
        return response['hits']['hits']
    
    except exceptions.BadRequestError as e:
        print(f"BadRequestError: {e.info}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


@transformer
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    index_name=kwargs.get("index_name")
    print(index_name)
    hits_results = search(
        connection_string='http://elastic_host:9200',
        index_name=index_name,
        source='text',
        question='When is the next cohort?'
    )
    if len(hits_results) > 0:
        return (hits_results[0],)
    return ({},)


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'