from pydantic import BaseModel, Field


class SocialUserCreateSchema(BaseModel):
    id: int = Field(..., gt=0)


class SocialUserSchema(BaseModel):
    id: int = Field(..., alias="_id")
    followers: list[int] = []
    following: list[int] = []
    tags: list[str] = []

    class Config:
        arbitrary_types_allowed = True
