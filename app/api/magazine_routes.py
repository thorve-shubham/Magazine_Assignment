from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.magazine import MagazineBase, MagazineResponse
from app.services.magazine_service import save_magazine, query_magazine, hybrid_search

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/magazine", response_model=List[MagazineBase], status_code=status.HTTP_201_CREATED)
def store_magazines(magazine_data: List[MagazineBase], db: Session = Depends(get_db)):
    try:
        logger.info("Received a request to store magazines.")
        saved_magazines = []

        for magazine in magazine_data:
            logger.debug(f"Processing magazine with title: {magazine.title}")
            saved_magazines.append(save_magazine(db, magazine))
            logger.debug(f"Magazine with title '{magazine.title}")

        logger.info(f"Total {len(saved_magazines)} magazines saved successfully.")
        return saved_magazines
    except Exception as e:
        logger.error(f"Error occurred while storing magazines: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/magazine", response_model=MagazineResponse, status_code=status.HTTP_200_OK)
def search_magazine(db: Session = Depends(get_db),
                    search: str = Query(None, description="Search query for magazines"),
                    page: int = Query(1, description="Search query for magazines"),
                    page_size: int = Query(10, description="Search query for magazines")):
    try:
        logger.info(f"Received a search request with query: '{search}', page: {page}, page_size: {page_size}")

        if not search:
            logger.warning("Search query is empty. Returning empty results.")
            return MagazineResponse(results=[], total_count=0)
        
        result = query_magazine(db=db, query=search, page=page, page_size=page_size)
        logger.info(f"Search completed successfully. Found {len(result.magazines)} results.")
        return result
    except Exception as e:
        logger.error(f"Error occurred during search: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/magazine/best", response_model=MagazineResponse, status_code=status.HTTP_200_OK)
def search_magazine(db: Session = Depends(get_db),
                    search: str = Query(None, description="Search query for magazines"),
                    page: int = Query(1, description="Search query for magazines"),
                    page_size: int = Query(10, description="Search query for magazines")):
    try:
        logger.info(f"Received a hybrid search request with query: '{search}', page: {page}, page_size: {page_size}")

        if not search:
            logger.warning("Search query is empty. Returning empty results.")
            return MagazineResponse(results=[], total_count=0)
        
        result = hybrid_search(db=db, query=search, page=page, page_size=page_size)
        logger.info(f"Hybrid search completed successfully. Found {len(result.magazines)} results.")
        return result
    except Exception as e:
        logger.error(f"Error occurred during hybrid search: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
