from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.Post import TagType


class SocialUserCreateSchema(BaseModel):
    id: int = Field(..., gt=0)


class SocialUserSchema(BaseModel):
    id: int = Field(..., alias="_id")
    followers: list[int] = []
    following: list[int] = []
    tags: list[str] = []

    class Config:
        arbitrary_types_allowed = True


class UserSchema(SocialUserSchema):
    name: Optional[str]
    photo: Optional[str]
    nickname: Optional[str]


class TagSchema(BaseModel):
    tag: TagType


class FollowUserSchema(BaseModel):
    user_id: int


class UserPartialUpdateSchema(BaseModel):
    followers: Optional[list[int]] = None
    following: Optional[list[int]] = None
    tags: Optional[list[str]] = None
