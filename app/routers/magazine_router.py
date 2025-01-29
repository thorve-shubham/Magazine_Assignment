from typing import List
from fastapi import APIRouter, Query, status, HTTPException
from app.model.magazine import Magazine
from app.services.magazine_service import MagazineService
from elasticsearch import exceptions as es_exceptions
import logging

# Initialize router
magazine_router = APIRouter()

logger = logging.getLogger(__name__)

@magazine_router.post("/", status_code=status.HTTP_201_CREATED)
def post_magazine(magazines: List[Magazine]):
    try:
        logger.debug("Starting the process of saving magazines.")
        response = MagazineService.save_magazines(magazines)
        logger.info(f"Successfully saved {len(magazines)} magazines.")
        return response
    except es_exceptions.BadRequestError as e:
        logger.error(f"BadRequestError occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred: {str(e)}",
        )
    except es_exceptions.NotFoundError as e:
        logger.error(f"NotFoundError occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"An error occurred: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
    
@magazine_router.get("/", status_code=status.HTTP_200_OK)
def search_magazines(search: str = Query(None, description="Search query for magazines"), 
                    page: int = Query(1, description="Page number (starting from 1)"),
                    pagesize: int = Query(10, description="Number of items per page")):
    try:
        logger.info(f"Received Request for search query: {search}, page: {page}, pagesize: {pagesize}")
        response = MagazineService.get_combined_magazines(query_text=search, page=page, page_size=pagesize)
        logger.debug(f"Found {len(response['magazines'])} magazines for search query: {search}")
        return response
    except es_exceptions.BadRequestError as e:
        logger.error(f"BadRequestError occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred: {str(e)}",
        )
    except es_exceptions.NotFoundError as e:
        logger.error(f"NotFoundError occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"An error occurred: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )