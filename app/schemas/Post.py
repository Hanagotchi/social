from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.schemas import User


class PostCreateSchema(BaseModel):
    author_user_id: int = Field(..., example=1)
    content: str = Field(..., max_length=512)
    photo_links: Optional[list[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "author_user_id": 1,
                "content": (
                    "Mi buena petuña es hermosa. "
                    "Crece, crece y crece, "
                    "y en verano me da mandarinas."
                ),
                "photo_links": [
                    "https://example.com/photo1.jpg",
                    "https://example.com/photo2.jpg",
                ],
            }
        }


class PostSchema(BaseModel):
    id: str = Field(...)
    author: User = Field(...)
    content: str = Field(..., max_length=512)
    likes_count: int = Field(default=0)
    created_at: datetime
    updated_at: datetime
    photo_links: Optional[list[str]] = None

    class Config:
        arbitrary_types_allowed = True
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
                "photo_links": [
                    "https://example.com/photo1.jpg",
                    "https://example.com/photo2.jpg",
                ],
            }
        }


class PostPartialUpdateSchema(BaseModel):
    content: Optional[str] = Field(None)

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
