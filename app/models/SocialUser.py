from __future__ import annotations
from pydantic import Field
from app.models.base import Base, PyObjectId
from app.schemas.SocialUser import SocialUserCreateSchema


class SocialUser(Base):
    """
    This class represents a Social user model in the database.
    """

    __collectionname__ = "users"

    # id of real user in the microservice!
    id: int = Field(strict=False, alias="_id")
    followers: list[int] = []
    following: list[int] = []
    tags: list[str] = []

    class Config:
        allow_population_by_field_name = False
        arbitrary_types_allowed = True

    def __repr__(self) -> str:
        return (
            f"Post(id={self.id!r}, followers={self.followers!r}, "
            f"following={self.following!r}, tags={self.tags!r}"
        )

    @classmethod
    def from_pydantic(cls, pydantic_obj: SocialUserCreateSchema):
        id = pydantic_obj.id
        dict = pydantic_obj.model_dump(by_alias=True, exclude=["id"])

        # "_id" is the """PK""" in MongoDB
        dict["_id"] = id
        return SocialUser(**dict)
