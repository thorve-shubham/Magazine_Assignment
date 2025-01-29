from elasticsearch import Elasticsearch, exceptions as es_exceptions
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Elasticsearch client
es = Elasticsearch(hosts = [os.getenv("ELASTICSEARCH_URL")], 
                   ca_certs=os.getenv("CERT_PATH"),
                   basic_auth=(os.getenv("ELASTIC_USERNAME"),os.getenv("ELASTIC_PASSWORD")))

def create_index_if_not_exists(index_name: str, index_mapping: dict):
    try:
        if not es.indices.exists(index=index_name):
            # Create the index if it doesn't exist
            es.indices.create(index=index_name, body=index_mapping)
            print(f"Index '{index_name}' created successfully.")
        else:
            print(f"Index '{index_name}' already exists.")
    except es_exceptions.ConnectionError:
        raise ConnectionError("Elasticsearch connection failed")
    except Exception as e:
        raise Exception(e)
    
def save_to_index(index: str, document: dict, id: str = None):
    try:
        return es.index(index=index, id=id, document=document)
    except es_exceptions.ConnectionError:
        raise ConnectionError("Elasticsearch connection failed")
    except Exception as e:
        raise Exception(e)
    

def get_from_index(index: str, body: str):
    try:
        return es.search(index=index, body=body)
    except es_exceptions.BadRequestError as e:
        if "no documents to get" in str(e):
            print(e)
            raise es_exceptions.BadRequestError("No documents found in Elasticsearch for the provided query.")
        else:
            raise Exception(f"Bad Request Error: {str(e)}")
    except es_exceptions.NotFoundError as e:
        raise es_exceptions.NotFoundError(f"Index '{index}' not found or no matching documents: {str(e)}")
    except es_exceptions.ConnectionError:
        raise ConnectionError("Elasticsearch connection failed")
    except Exception as e:
        raise Exception(e)
    
def get_by_id_from_index(index:str, id: str):
    try:
        return es.get(index=index, id=id)
    except es_exceptions.BadRequestError as e:
        if "no documents to get" in str(e):
            raise es_exceptions.BadRequestError("No documents found in Elasticsearch for the provided query.")
        else:
            raise Exception(f"Bad Request Error: {str(e)}")
    except es_exceptions.BadRequestError as e:
        raise es_exceptions.BadRequestError(f"No documents found for the given query: {str(e)} in Index: {index}")
    except es_exceptions.NotFoundError as e:
        raise es_exceptions.NotFoundError(f"Index '{index}' not found or no matching documents: {str(e)}")
    except es_exceptions.ConnectionError:
        raise ConnectionError("Elasticsearch connection failed")
    except Exception as e:
        raise Exception(e)
    
def get_by_mget(body):
    try:
        return es.mget(body=body)
    except es_exceptions.BadRequestError as e:
        if "no documents to get" in str(e):
            raise es_exceptions.BadRequestError("No documents found in Elasticsearch for the provided query.")
        else:
            raise Exception(f"Bad Request Error: {str(e)}")
    except es_exceptions.ConnectionError:
        raise ConnectionError("Elasticsearch connection failed")
    except Exception as e:
        raise Exception(e)