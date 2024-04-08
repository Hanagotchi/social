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
    id_user: int = Field(...)
    content: str = Field(..., max_length=512)
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        allow_population_by_field_name = False
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    def __repr__(self) -> str:
        return (
            f"Publication(id={self.id!r}, id_user={self.id_user!r}, "
            f"content={self.content!r}), created_at={self.created_at!r}, "
            f"updated_at={self.updated_at!r}"
        )

    @classmethod
    def from_pydantic(cls, pydantic_obj: PublicationCreateSchema):
        return Publication(
            id_user=pydantic_obj.id_user,
            content=pydantic_obj.content,
            created_at=None,
            updated_at=None,
        )
