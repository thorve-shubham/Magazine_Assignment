from fastapi import FastAPI
from app.routers.magazine_router import magazine_router
from app.utils.elasticsearch_utils import create_index_if_not_exists
from app.utils.index_mappings import magazine_content_mapping, magazine_information_mapping
import uvicorn
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create indices if they do not exist
try:
    logger.debug("Checking and creating Elasticsearch indices if not present.")
    create_index_if_not_exists("magazine_information", magazine_information_mapping)
    create_index_if_not_exists("magazine_content", magazine_content_mapping)
    logger.info("Elasticsearch indices created or already exist.")
except Exception as e:
    logger.error(f"Error occurred while creating indices: {str(e)}")

# Initialize FastAPI app
app = FastAPI()

# Include the magazine router
app.include_router(magazine_router, prefix="/magazines", tags=["magazines"])

try:
    logger.info("Starting FastAPI application on host: 0.0.0.0, port: 8000.")
    uvicorn.run(app, host="0.0.0.0", port=8000)
except Exception as e:
    logger.error(f"Error occurred while running the FastAPI application: {str(e)}")