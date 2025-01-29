from typing import List
from uuid import uuid4

from elasticsearch import exceptions as es_exceptions
from fastapi import HTTPException
from streamlit import status
from app.model.magazine import Magazine
from app.utils.elasticsearch_utils import save_to_index, get_from_index, get_by_mget
from app.utils.embedding_generator import generate_embeddings

import logging

logger = logging.getLogger(__name__)

class MagazineService:

    @staticmethod
    def save_magazines(magazines: List[Magazine]):
        saved_magazines = []
        errors = []

        for magazine in magazines:
            try:
                # Generate a unique ID for the magazine
                magazine_id = str(uuid4())
                logger.debug(f"Generated unique ID {magazine_id} for magazine: {magazine.title}")
                # Save magazine data to the 'magazine_information' index
                magazine_doc = {
                    "id": magazine_id,
                    "title": magazine.title,
                    "author": magazine.author,
                    "publish_date": magazine.publish_date,
                    "category": magazine.category,
                }
                save_to_index("magazine_information", magazine_doc, magazine_id)
                logger.info(f"Saved magazine information for {magazine.title}")
                # Generate embeddings for the content
                embeddings = generate_embeddings(magazine.content)
                logger.debug(f"Generated embeddings for magazine: {magazine.title}")
                # Save embeddings to the 'magazine_content' index
                embeddings_doc = {
                    "id": str(uuid4()),
                    "magazine_id": magazine_id,
                    "embeddings": embeddings,
                    "content": magazine.content
                }
                save_to_index("magazine_content", embeddings_doc)
                logger.info(f"Saved embeddings for {magazine.title}")

                saved_magazines.append({"magazine_id": magazine_id, "message": "Saved successfully"})

            except es_exceptions.RequestError as e:
                errors.append({"magazine": magazine.title, "error": f"Invalid request: {str(e)}"})
                logger.error(f"Error saving magazine {magazine.title}: Invalid request - {str(e)}")
            except es_exceptions.ConnectionError:
                errors.append({"magazine": magazine.title, "error": "Failed to connect to Elasticsearch."})
                logger.error(f"Error saving magazine {magazine.title}: Failed to connect to Elasticsearch.")
            except Exception as e:
                errors.append({"magazine": magazine.title, "error": f"Unexpected error: {str(e)}"})
                logger.error(f"Unexpected error while saving magazine {magazine.title}: {str(e)}")

        # If any errors occurred, raise an exception with error details
        if errors:
            logger.warning(f"Some magazines failed to save: {str(errors)}")
            raise HTTPException(f"Some magazines failed to save : {str(errors)}")
        
        logger.info(f"All magazines saved successfully: {len(saved_magazines)}")
        return {"message": "All magazines saved successfully", "saved_magazines": saved_magazines}

    @staticmethod
    def get_magazines_by_embedding(query_text, top_k=5, page=1, page_size=10):
        try:
            # Generate embeddings for the query text
            query_embedding = generate_embeddings(query_text)

            # Calculate the starting index for pagination
            start_from = (page - 1) * page_size
            logger.debug(f"Pagination: start_from={start_from}, page_size={page_size}")
            # Elasticsearch `knn` query for vector search
            query = {
                "knn": {
                    "field": "embeddings",  # The field containing the embeddings
                    "query_vector": query_embedding,  # The query embedding
                    "k": top_k,  # Number of nearest neighbors to retrieve
                    "num_candidates": 100  # Number of candidates to consider
                },
                "from": start_from,  # Pagination: starting index
                "size": page_size    # Pagination: number of results per page
            }

            # Execute the query on the `magazine_content` index
            response = get_from_index(index="magazine_content", body=query)
            logger.info(f"Executed knn query on magazine_content, found {len(response['hits']['hits'])} hits")

            if "hits" in response and "hits" in response["hits"]:
                if len(response['hits']['hits']) == 0:
                    return {
                        "magazines" : []
                    }

            # Extract the magazine IDs from the response
            magazine_ids = [hit["_source"]["magazine_id"] for hit in response["hits"]["hits"]]
            logger.debug(f"Found magazine IDs: {magazine_ids}")

            # Use `_mget` to fetch all magazine details from the `magazine_information` index in one request
            mget_body = {
                "docs": [
                    {"_index": "magazine_information", "_id": magazine_id}
                    for magazine_id in magazine_ids
                ]
            }

            mget_response = get_by_mget(body=mget_body)
            logger.info(f"Executed _mget query, fetched details for {len(mget_response['docs'])} magazines")

            # Extract magazine details from the `_mget` response
            magazines = [doc["_source"] for doc in mget_response["docs"] if doc["found"]]

            # Return the magazines and pagination metadata
            total_hits = response["hits"]["total"]["value"]
            total_pages = (total_hits + page_size - 1) // page_size  # Calculate total pages
            logger.debug(f"Pagination: total_hits={total_hits}, total_pages={total_pages}")

            return {
                "magazines": magazines,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_results": total_hits,
                    "total_pages": total_pages
                }
            }
        except es_exceptions.BadRequestError as e:
            logger.error(f"BadRequestError: {str(e)}")
            raise es_exceptions.BadRequestError(e)
        except es_exceptions.NotFoundError as e:
            logger.error(f"NotFoundError: {str(e)}")
            raise es_exceptions.NotFoundError(e)
        except es_exceptions.ConnectionError as e:
            logger.error(f"ConnectionError: {str(e)}")
            raise ConnectionError(e)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise Exception(e)
    
    @staticmethod
    def get_magazines(query_text, page=1, page_size=10):
        try:
            # Calculate the starting index for pagination
            start_from = (page - 1) * page_size
            logger.debug(f"Pagination: start_from={start_from}, page_size={page_size}")
            # Elasticsearch query for normal search on title, author, and category
            query = {
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"title": query_text}},  # Search in the title field
                            {"match": {"author": query_text}},  # Search in the author field
                            {"match": {"category": query_text}}  # Search in the category field
                        ],
                        "minimum_should_match": 1  # At least one of the fields should match
                    }
                },
                "from": start_from,  # Pagination: starting index
                "size": page_size    # Pagination: number of results per page
            }

            # Execute the query on the `magazine_information` index
            response = get_from_index(index="magazine_information", body=query)
            logger.info(f"Executed query on magazine_information, found {len(response['hits']['hits'])} hits")
            # Extract the magazine details from the response
            magazines = [hit["_source"] for hit in response["hits"]["hits"]]

            # Calculate total hits for pagination metadata
            total_hits = response["hits"]["total"]["value"]
            total_pages = (total_hits + page_size - 1) // page_size  # Calculate total pages
            logger.debug(f"Pagination: total_hits={total_hits}, total_pages={total_pages}")

            # Return the magazines and pagination metadata
            return {
                "magazines": magazines,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_results": total_hits,
                    "total_pages": total_pages
                }
            }
        
        except es_exceptions.BadRequestError as e:
            logger.error(f"BadRequestError: {str(e)}")
            raise es_exceptions.BadRequestError(e)
        except es_exceptions.NotFoundError as e:
            logger.error(f"NotFoundError: {str(e)}")
            raise es_exceptions.NotFoundError(e)
        except es_exceptions.ConnectionError as e:
            logger.error(f"ConnectionError: {str(e)}")
            raise es_exceptions.ConnectionError(e)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise Exception(e)
    
    @staticmethod
    def get_combined_magazines(query_text, top_k=5, page=1, page_size=10):
        try:
            # Get results from both methods page_size * 2 to get enough results from both search strategies
            embedding_results = MagazineService.get_magazines_by_embedding(query_text, top_k=top_k, page=page, page_size=page_size*2)
            logger.info(f"Found {len(embedding_results)} matching magzines via embeddings")
            normal_results = MagazineService.get_magazines(query_text, page=page, page_size=page_size*2)
            logger.info(f"Found {len(normal_results)} matching magzines basic search")

            # Combine and remove duplicates based on 'id' (assuming id is unique for each magazine)
            seen_ids = set()
            combined_magazines = []

            for magazine in embedding_results["magazines"] + normal_results["magazines"]:
                magazine_id = magazine["id"]  # Assuming "id" is present in magazine documents
                if magazine_id not in seen_ids:
                    seen_ids.add(magazine_id)
                    combined_magazines.append(magazine)
                
            logger.info(f"Total {len(seen_ids)} unique magazines found...")

            # Calculate total results and apply pagination
            total_results = len(combined_magazines)
            total_pages = (total_results + page_size - 1) // page_size

            # Paginate the merged results
            start_index = (page - 1) * page_size
            paginated_results = combined_magazines[start_index: start_index + page_size]

            # Return final combined results with pagination metadata
            return {
                "magazines": paginated_results,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_results": total_results,
                    "total_pages": total_pages
                }
            }
        except es_exceptions.BadRequestError as e:
            raise es_exceptions.BadRequestError(e)
        except es_exceptions.NotFoundError:
            raise  es_exceptions.NotFoundError(e)
        except es_exceptions.ConnectionError:
            raise es_exceptions.ConnectionError (e)
        except Exception as e:
            raise Exception(e)