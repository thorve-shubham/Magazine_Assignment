from fastapi import FastAPI
import uvicorn
from app.api.magazine_routes import router as magazine_router
from app.database import engine, Base
from app.util.utils import create_indexes

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

#create required indexes
create_indexes()

app = FastAPI(title="Magazine API")

# Include the API router
app.include_router(magazine_router, prefix="/api", tags=["magazines"])

try:
    logger.info("Starting FastAPI application on host: 0.0.0.0, port: 8000.")
    uvicorn.run(app, host="0.0.0.0", port=8000)
except Exception as e:
    logger.error(f"Error occurred while running the FastAPI application: {str(e)}")