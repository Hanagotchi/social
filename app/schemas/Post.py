from pydantic import BaseModel, Field, AfterValidator, HttpUrl, model_validator
from typing import Annotated, Any, Optional
from app.schemas.RealUser import ReducedUser
from datetime import datetime

PhotoUrl = Annotated[HttpUrl, AfterValidator(lambda v: str(v))]

TagType = Annotated[str, Field(..., min_length=2,
                               max_length=128,
                               pattern=r"^[a-zA-Z0-9_]*$")]


class PostCreateSchema(BaseModel):
    author_user_id: int = Field(..., example=1)
    content: str = Field(..., max_length=512)
    tags: Optional[list[TagType]] = None
    photo_links: Optional[list[PhotoUrl]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "author_user_id": 1,
                "content": (
                    "Mi buena petuña es hermosa. "
                    "Crece, crece y crece, "
                    "y en verano me da mandarinas."
                ),
                "photo_links": [
                    "https://example.com/photo1.jpg",
                    "https://example.com/photo2.jpg",
                ],
                "tags": ["petuñas", "mandarinas"],
            }
        }


class PostBaseModel(BaseModel):
    id: str = Field(...)
    author: ReducedUser = Field(...)
    content: str = Field(..., max_length=512)
    likes_count: int = Field(default=0)
    users_who_gave_like: list[int] = Field(default=[])
    liked_by_me: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime
    tags: Optional[list[TagType]] = None

"""     @model_validator(mode='before')
    @classmethod
    def check_if_post_has_been_liked_by_requestor(cls, data: Any) -> Any:
        if isinstance(data, dict):
            requestor_id = data.pop("requestor_id", None)
            if requestor_id:
                data["liked_by_me"] = any(
                    map(
                        lambda id: id == requestor_id,
                        data["users_who_gave_like"]
                    )
                )

        return data """


class PostSchema(PostBaseModel):
    photo_links: Optional[list[PhotoUrl]] = None

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "author_user_id": 1,
                "content": (
                    "Mi buena petuña es hermosa. "
                    "Crece, crece y crece, "
                    "y en verano me da mandarinas."
                ),
                "likes_count": 0,
                "created_at": "2021-08-08T20:00:00",
                "updated_at": "2021-08-08T20:00:00",
                "tags": ["petuñas", "mandarinas"],
                "photo_links": [
                    "https://example.com/photo1.jpg",
                    "https://example.com/photo2.jpg",
                ],
            }
        }
        # datetime.now(
        #                         ZoneInfo("America/Argentina/Buenos_Aires")
        #                     ).isoformat()[:-6]
        # json_encoders = {datetime: lambda v: datetime.now(
        #                         ZoneInfo("America/Argentina/Buenos_Aires")
        #                     ).isoformat()[:-6]}


class PostInFeedSchema(PostBaseModel):
    main_photo_link: Optional[PhotoUrl] = None

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "author_user_id": 1,
                "content": (
                    "Mi buena petuña es hermosa. "
                    "Crece, crece y crece, "
                    "y en verano me da mandarinas."
                ),
                "likes_count": 0,
                "created_at": "2021-08-08T20:00:00",
                "updated_at": "2021-08-08T20:00:00",
                "tags": ["petuñas", "mandarinas"],
                "main_photo_link": "https://example.com/photo1.jpg",
            }
        }

    @classmethod
    def from_post(cls, post: PostSchema):
        dict = post.model_dump()
        dict["main_photo_link"] = (
            dict["photo_links"][0] if dict["photo_links"] else None
        )
        return cls(**dict)


class PostPartialUpdateSchema(BaseModel):
    content: Optional[str] = Field(None, max_length=512)
    tags: Optional[list[TagType]] = None
    photo_links: Optional[list[PhotoUrl]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "content": (
                    "Mi buena petuña es hermosa. "
                    "Crece, crece y crece, "
                    "y en verano me da mandarinas."
                ),
                "tags": ["petuñas", "mandarinas"],
                "photo_links": [
                    "https://example.com/photo5520.jpg",
                    "https://example.com/photo123.jpg",
                ],
            }
        }


class PostPagination(BaseModel):
    time_offset: datetime
    page: int
    per_page: int


class PostFilters(BaseModel):
    pagination: PostPagination
    users: Optional[list[int]] = None
    tags: Optional[str] = Field(..., min_length=2, max_length=128)
