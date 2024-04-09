from __future__ import annotations
from typing import Optional
from bson import ObjectId
from pydantic import Field
from app.models.base import Base, PyObjectId
from app.schemas.Publication import PublicationCreateSchema
from datetime import datetime


class Publication(Base):
    __collectionname__ = "publications"

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    author_user_id: int = Field(...)
    content: str = Field(..., max_length=512)
    likes_count: int = Field(default=0)
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        allow_population_by_field_name = False
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    def __repr__(self) -> str:
        return (
            f"Publication(id={self.id!r}, author_user_id={self.author_user_id!r}, "
            f"content={self.content!r}), created_at={self.created_at!r}, "
            f"updated_at={self.updated_at!r}"
        )

    @classmethod
    def from_pydantic(cls, pydantic_obj: PublicationCreateSchema):
        return Publication(
            author_user_id=pydantic_obj.author_user_id,
            content=pydantic_obj.content,
            created_at=None,
            updated_at=None,
        )
