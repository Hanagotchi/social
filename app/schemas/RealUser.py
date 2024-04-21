from pydantic import BaseModel
from typing import Dict, Optional
from datetime import date


class GetUserSchema(BaseModel):
    """
    Schema used to model the response of the `GET /users/{user_id}`endpoint
    """

    id: int
    name: Optional[str]
    email: Optional[str]
    gender: Optional[str]
    photo: Optional[str]
    birthdate: Optional[date]
    location: Optional[Dict]
    nickname: Optional[str]
    biography: Optional[str]


class ReducedUser(BaseModel):
    """
    Schema used to display the minimal and necessary information of a user in a post.
    """

    id: Optional[int]
    name: Optional[str]
    photo: Optional[str]
    nickname: Optional[str]

    @classmethod
    def from_pydantic(cls, pydantic_obj: GetUserSchema):
        return ReducedUser(
            id=pydantic_obj.id,
            name=pydantic_obj.name,
            photo=pydantic_obj.photo,
            nickname=pydantic_obj.nickname,
        )
