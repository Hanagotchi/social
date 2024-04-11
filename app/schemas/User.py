from pydantic import BaseModel
from typing import Dict, Optional
from datetime import date


class GetUserSchema(BaseModel):
    id: int
    name: Optional[str]
    email: Optional[str]
    gender: Optional[str]
    photo: Optional[str]
    birthdate: Optional[date]
    location: Optional[Dict]
    nickname: Optional[str]
    biography: Optional[str]


class User(BaseModel):
    id: int
    name: Optional[str]
    photo: Optional[str]
    nickname: Optional[str]

    @classmethod
    def from_pydantic(cls, pydantic_obj: GetUserSchema):
        return User(
            id=pydantic_obj.id,
            name=pydantic_obj.name,
            photo=pydantic_obj.photo,
            nickname=pydantic_obj.nickname,
        )
