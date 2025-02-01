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
        saved_magazines = []
        for magazine in magazine_data:
            logger.info(f"Received a request to save a magazine: {magazine.title}")
            saved_magazines.append(save_magazine(db, magazine))
        return saved_magazines
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/magazine", response_model=MagazineResponse, status_code=status.HTTP_200_OK)
def search_magazine(db: Session = Depends(get_db),
                    search: str = Query(None, description="Search query for magazines"),
                    page: int = Query(1, description="Search query for magazines"),
                    page_size: int = Query(10, description="Search query for magazines")):
    try:
        logger.info(f"Received a search request with query : {search}, page: {page}, page_size: {page_size}", )
        return query_magazine(db=db,query=search, page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/magazine/best", response_model=MagazineResponse, status_code=status.HTTP_200_OK)
def search_magazine(db: Session = Depends(get_db),
                    search: str = Query(None, description="Search query for magazines"),
                    page: int = Query(1, description="Search query for magazines"),
                    page_size: int = Query(10, description="Search query for magazines")):
    try:
        logger.info(f"Received a search request with query : {search}, page: {page}, page_size: {page_size}", )
        return hybrid_search(db=db,query=search, page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/magazine/analyze", status_code=status.HTTP_200_OK)
def search_magazine(db: Session = Depends(get_db),
                    search: str = Query(None, description="Search query for magazines"),
                    page: int = Query(1, description="Search query for magazines"),
                    page_size: int = Query(10, description="Search query for magazines")):
    try:
        logger.info(f"Received a search request with query : {search}, page: {page}, page_size: {page_size}", )
        return analyze_combined_search(db=db,query=search, page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
