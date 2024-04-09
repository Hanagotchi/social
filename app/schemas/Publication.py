from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PublicationCreateSchema(BaseModel):
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


class PublicationSchema(BaseModel):
    id: str = Field(...)
    author_user_id: int = Field(..., example=1)
    content: str = Field(..., max_length=512)
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
                "created_at": "2021-08-08T20:00:00",
                "updated_at": "2021-08-08T20:00:00",
            }
        }


class PublicationPartialUpdateSchema(BaseModel):
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
