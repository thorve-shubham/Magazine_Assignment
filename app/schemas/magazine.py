from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime, date

class MagazineBase(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., min_length=3, max_length=100, description="Title must be between 3 and 100 characters.")
    author: str = Field(..., min_length=3, max_length=50, description="Author name must be between 3 and 50 characters.")
    category: str = Field(..., min_length=3, max_length=30, description="Category must be between 3 and 30 characters.")
    publish_date: date = Field(..., description="Date must be in YYYY-MM-DD format.")
    content: str = Field(..., min_length=10, description="Content must be at least 10 characters long.")
    
class MagazineResponse(BaseModel):
    magazines: List[MagazineBase]
    page: int
    page_size: int
    total_results: Optional[int] = None
    total_pages: Optional[int] = None