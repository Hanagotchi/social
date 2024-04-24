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

class UserSchema(SocialUserSchema):
    name: Optional[str]
    photo: Optional[str]
    nickname: Optional[str]


class FollowUserSchema(BaseModel):
    user_id: int


class UserPartialUpdateSchema(BaseModel):
    followers: Optional[list[int]] = None
    following: Optional[list[int]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "followers": [1, 2],
                "following": [2, 3, 6],
            }
        }
