# Index mappings for 'magazines' and 'magazines_embeddings'
magazine_information_mapping = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "title": {"type": "text"},
            "author": {"type": "text"},
            "publish_date": {"type": "date"},
            "category": {"type": "keyword"},
        }
    }
}

magazine_content_mapping = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "magazine_id": {"type": "keyword"},
            "embeddings": {"type": "dense_vector", "dims": 768, "index": True, "similarity": "l2_norm"},  # dimension for embeddings using all-mpnet-base-v2 model
        }
    }
}