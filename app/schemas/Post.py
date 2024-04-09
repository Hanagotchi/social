from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PostCreateSchema(BaseModel):
    author_user_id: int = Field(..., example=1)
    content: str = Field(..., max_length=512)

    class Config:
        json_schema_extra = {
            "example": {
                "author_user_id": 1,
                "content": (
                    "Mi buena petuña es hermosa. "
                    "Crece, crece y crece, "
                    "y en verano me da mandarinas."
                ),
            }
        }


class PostSchema(BaseModel):
    id: str = Field(...)
    author_user_id: int = Field(..., example=1)
    content: str = Field(..., max_length=512)
    likes_count: int = Field(default=0)
    author_user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "author_user_id": 1,
                "content": (
                    "Mi buena petuña es hermosa. "
                    "Crece, crece y crece, "
                    "y en verano me da mandarinas."
                ),
                "likes_count": 0,
                "created_at": "2021-08-08T20:00:00",
                "updated_at": "2021-08-08T20:00:00",
            }
        }


class PostPartialUpdateSchema(BaseModel):
    content: Optional[str] = Field(..., max_length=512)

    class Config:
        json_schema_extra = {
            "example": {
                "content": (
                    "Mi buena petuña es hermosa. "
                    "Crece, crece y crece, "
                    "y en verano me da mandarinas."
                ),
            }
        }
