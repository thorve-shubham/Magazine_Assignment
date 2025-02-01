from sqlalchemy import text
from sqlalchemy.orm import Session
from app.repositories.magazine_repository import create_magazine, keyword_search, vector_search, combined_search
from app.schemas.magazine import MagazineBase, MagazineResponse

import logging

from app.util.utils import get_embeddings

logger = logging.getLogger(__name__)

# saving magazine to the database
def save_magazine(db: Session, magazine_data: MagazineBase):
    try:
        logger.info("Saving magazine to the database: %s", magazine_data.title)
        return create_magazine(db, magazine_data)
    except Exception as e:
        logger.error("Error in save_magazine: %s", str(e))
        raise Exception(f"Error in save_magazine: {e}")

# A basic approach of querying information seperately and then performing deduplication ---> Less Efficient 
# as paging will be inefficient and will query huge data unncessarily
def query_magazine(db: Session, query: str, page: int = 1, page_size: int = 10):
    try:
        logger.debug("Querying magazine with search term: '%s' | Page: %d | Page Size: %d", query, page, page_size)
        # Fetch all results with 2*page_size as we might fetch duplicate magazines 
        keyword_search_results = keyword_search(db=db, query=query, page=page, page_size=page_size*2)
        logger.debug("Keyword search fetched %d results", len(keyword_search_results))
        vector_search_results = vector_search(db=db, query=query, page=page, page_size=page_size*2)
        logger.debug("Vector search fetched %d results", len(vector_search_results))
        # Merge both result sets
        combined_results = keyword_search_results + vector_search_results
        logger.debug("Total combined results before deduplication: %d", len(combined_results))

        # Deduplicate by magazine_id (keeping highest-scored one)
        unique_magazines = {}
        for result in combined_results:
            magazine_id = result.id
            if magazine_id not in unique_magazines:
                unique_magazines[magazine_id] = {
                    "id": result.id,
                    "title": result.title,
                    "author": result.author,
                    "category": result.category,
                    "publish_date": result.publish_date,
                    "content": result.content,
                    "score": result.score
                }
            else:
                if unique_magazines[magazine_id]["score"] < result.score:
                    unique_magazines[magazine_id] = {
                        "id": result.id,
                        "title": result.title,
                        "author": result.author,
                        "category": result.category,
                        "publish_date": result.publish_date,
                        "content": result.content
                    }

        # Convert dictionary to list (sorted)
        sorted_unique_magazines = list(unique_magazines.values())
        logger.info("Total unique magazines after deduplication: %d", len(sorted_unique_magazines))
        # Apply pagination **after deduplication**
        offset = (page - 1) * page_size
        paginated_results = sorted_unique_magazines[offset:offset + page_size]

        # Convert to JSON-friendly format
        magazines = [
            MagazineBase(
                id=magzine['id'],
                title=magzine['title'],
                author=magzine['author'],
                category=magzine['category'],
                publish_date=magzine['publish_date'],
                content=magzine['content']
            )
            for magzine in paginated_results
        ]

        logger.info("Returning %d paginated results", len(magazines))

        # Return paginated response
        return MagazineResponse(
            magazines=magazines,
            page=page,
            page_size=page_size,
            total_results=len(sorted_unique_magazines),
            total_pages= len(sorted_unique_magazines) // page_size
        )

    except Exception as e:
        logger.error("Error in query_magazine: %s", str(e))
        raise Exception(f"Error in query_magazine: {e}")
    

def hybrid_search(db: Session, query: str, page: int = 1, page_size: int = 10):
    try:
        logger.debug("Performing hybrid search with query: '%s' | Page: %d | Page Size: %d", query, page, page_size)
        results = combined_search(db=db,query=query,page=page,page_size=page_size)
        logger.debug("Hybrid search fetched %d results", len(results))
        magazines = [
            MagazineBase(
                id=row.id,
                title=row.title,
                author=row.author,
                category=row.category,
                publish_date=row.publish_date,
                content=row.content
            )
            for row in results
        ]

        logger.info("Returning %d results from hybrid search", len(magazines))

        return MagazineResponse(
            magazines=magazines,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error("Error in hybrid_search: %s", str(e))
        raise Exception(f"Error in hybrid_search: {e}")



