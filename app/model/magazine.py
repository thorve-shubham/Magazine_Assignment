from pydantic  import BaseModel, Field, validator
from datetime import datetime

class Magazine(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=50)
    publish_date: str
    category: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1)

    # Validate publish_date format (YYYY-MM-DD)
    @validator("publish_date")
    def validate_publish_date(cls, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("publish_date must be in the format YYYY-MM-DD")
        return value