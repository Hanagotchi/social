from pydantic import BaseModel, Field
from typing import Optional


class SocialUserCreateSchema(BaseModel):
    id: int = Field(..., gt=0)


class SocialUserSchema(BaseModel):
    id: int = Field(..., alias="_id")
    followers: list[int] = []
    following: list[int] = []
    tags: list[str] = []

    class Config:
        arbitrary_types_allowed = True


class UserPartialUpdateSchema(BaseModel):
    followers: Optional[list[int]] = None
    following: Optional[list[int]] = None
