from sqlalchemy import func, text
from sqlalchemy.orm import Session
from app.model.magazine import MagazineInformation, MagazineContent
from app.schemas.magazine import MagazineBase
from app.util.utils import get_embeddings
from pgvector.sqlalchemy import Vector
import numpy as np
import logging


logger = logging.getLogger(__name__)

def create_magazine(db: Session, magazine_data: MagazineBase):
    try:
        logger.info("Creating a new magazine entry.")
        new_magazine = MagazineInformation(
            title=magazine_data.title,
            author=magazine_data.author,
            category=magazine_data.category,
            publish_date=magazine_data.publish_date,
        )

        db.add(new_magazine)
        db.commit()
        db.refresh(new_magazine)

        logger.info(f"New magazine created with ID: {new_magazine.id}")

        new_content = MagazineContent(
            magazine_id=new_magazine.id,
            content=magazine_data.content,
            content_embedding = get_embeddings(magazine_data.content),
            content_tsvector=text("to_tsvector('english', :b_content)").bindparams(b_content=magazine_data.content)
        )
        db.add(new_content)
        db.commit()
        
        magazine_data.id = new_magazine.id
        logger.info("Magazine content added successfully.")
        return magazine_data
    
    except Exception as e:
        raise Exception(e)

# A seperate method for keyword based search on author, title and content_tsvector field  
def keyword_search(db: Session,query: str,page: int=1,page_size: int=10):
    try:
        logger.info(f"Performing keyword search for query: {query}")

        offset = (page - 1) * page_size

        text_search = func.to_tsquery('english', query.replace(' ', ' | '))

        rank_expr = func.ts_rank_cd(MagazineContent.content_tsvector, text_search)

        query = db.query(
            MagazineInformation.id,
            MagazineInformation.title,
            MagazineInformation.author,
            MagazineInformation.category,
            MagazineInformation.publish_date,
            MagazineContent.content,
            rank_expr.label("score")
        ).join(
            MagazineContent, MagazineInformation.id == MagazineContent.magazine_id
        ).filter(
            # Full-text search for content_tsvector
            text_search.op("@@")(MagazineContent.content_tsvector) |
            # Title and author search using ILIKE for case-insensitive matching
            func.lower(MagazineInformation.title).like(f"%{query.lower()}%") |
            func.lower(MagazineInformation.author).like(f"%{query.lower()}%")
        ).order_by(
            # Order by text relevance score
            rank_expr.desc()
        ).limit(page_size).offset(offset)

        results = query.all()
        logger.info(f"Keyword search returned {len(results)} results.")
        return results
    
    except Exception as e:
        logger.error(f"Error during keyword search: {e}")
        raise Exception(e)


# A seperate method for vector search with pagination and min score threshold to avoid irrelevant documents
def vector_search(db: Session, query: str, page: int = 1, page_size: int = 10, min_score: float = 0.15):
    try:
        logger.info(f"Performing vector search for query: {query}")
        query_vector = get_embeddings(query).tolist() 

        query_vector = func.cast(query_vector, Vector(384))

        offset = (page - 1) * page_size

        # Cosine distance calculation (1 - cosine similarity)
        similarity_score = 1 - func.cosine_distance(MagazineContent.content_embedding, query_vector)

        query = db.query(
            MagazineInformation.id,
            MagazineInformation.title,
            MagazineInformation.author,
            MagazineInformation.category,
            MagazineInformation.publish_date,
            MagazineContent.content,
            similarity_score.label("score")
        ).join(
            MagazineContent, MagazineInformation.id == MagazineContent.magazine_id
        ).filter(
            similarity_score >= min_score
        ).order_by(
            similarity_score.desc()  # Higher similarity scores first
        ).limit(page_size).offset(offset)

        results = query.all()
        logger.info(f"Vector search returned {len(results)} results.")
        return results
    
    except Exception as e:
        logger.error(f"Error during vector search: {e}")
        raise Exception(e)



# An efficient apporoach to perform combines search, sorting, paging and deduplication at database level
def combined_search(db: Session, query: str, page: int = 1, page_size: int = 10, min_score: float = 0.15):
    try:
        logger.info(f"Performing combined search for query: {query}")
        query_vector = get_embeddings(query)
        query_vector = np.array(query_vector, dtype=np.float32)
        # convert np.array float32 to string
        query_embedding_str = "[" + ",".join(map(str, query_vector.tolist())) + "]"

        offset = (page - 1) * page_size

        sql_query = text(f"""
            WITH keyword_search AS (
                    SELECT 
                        mi.id, mi.title, mi.author, mi.category, mi.publish_date,
                        mc.content,
                        ts_rank_cd(mc.content_tsvector, to_tsquery('english', :query)) AS score
                    FROM magazine_information mi
                    JOIN magazine_content mc ON mi.id = mc.magazine_id
                    WHERE (mc.content_tsvector @@ to_tsquery('english', :query))
                    OR mi.title % :query
                    OR mi.author % :query
                    OR mi.title ILIKE '%' || :query || '%' 
                    OR mi.author ILIKE '%' || :query || '%'
                ),
                vector_search AS (
                    SELECT * FROM (
                        SELECT 
                            mi.id, mi.title, mi.author, mi.category, mi.publish_date,
                            mc.content,
                            (1 - (mc.content_embedding <=> :query_embedding)) AS score
                        FROM magazine_information mi
                        JOIN magazine_content mc ON mi.id = mc.magazine_id
                    ) subquery
                    WHERE score >= :threshold 
                    ORDER BY score DESC
                ),
                combined_results AS (
                    SELECT * FROM keyword_search
                    UNION ALL
                    SELECT * FROM vector_search
                )
                SELECT DISTINCT ON (id) *
                FROM combined_results
                ORDER BY id, score DESC
                LIMIT :page_size OFFSET :offset;
        """)

        # Execute the query with parameters
        results = db.execute(sql_query, {
            "query": query.replace(" ", " | "),
            "query_embedding": query_embedding_str,
            "threshold": min_score,
            "page_size": page_size,
            "offset": offset,
        }).fetchall()

        logger.info(f"Combined search returned {len(results)} results.")
        return results
    
    except Exception as e:
        logger.error(f"Error during combined search: {e}")
        raise Exception(e)