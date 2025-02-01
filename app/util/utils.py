from sentence_transformers import SentenceTransformer
from sqlalchemy import inspect, text
from app.database import engine

import logging

logger = logging.getLogger(__name__)

model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")  

def get_embeddings(text: str):
    return model.encode(text)

def create_indexes():
    try:
        with engine.connect() as connection:
            # Create HNSW indexes for content_embedding
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_content_embedding_cosine
                ON magazine_content USING hnsw (content_embedding vector_cosine_ops);
            """))
            logger.info('HNSW index (Vector Cosine) created successfully.')

            # Create indexes for magazine_information
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_magazine_title
                ON magazine_information (title);
            """))
            logger.info('Index for magazine_information --> title created successfully.')
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_magazine_author
                ON magazine_information (author);
            """))
            logger.info('Index for magazine_information --> author created successfully.')
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_magazine_title_trgm ON magazine_information USING GIN(title gin_trgm_ops);
            """))
            logger.info('Index (GIN+TRIGRAM) for magazine_content --> title created successfully.')

            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_magazine_author_trgm ON magazine_information USING GIN(author gin_trgm_ops);
            """))
            logger.info('Index GIN+TRIGRAM for magazine_information --> Author created successfully.')

            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS content_tsvector_idx ON magazine_content USING GIN(content_tsvector);
            """))
            logger.info('Index (GIN) for magazine_content --> content_tsvector created successfully.')

            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_score ON magazine_content USING btree(content_embedding);
            """))
            logger.info('Index (B-TREE) for magazine_content --> content_embedding created successfully.')

            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_magazine_id ON magazine_content(magazine_id);
            """))
            logger.info('Indexes for magazine_content --> magazine_id created successfully.')

    except Exception as error:
        logger.error(f'Error creating indexes: {error}')
        raise error