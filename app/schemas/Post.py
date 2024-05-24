from pydantic import BaseModel, Field, AfterValidator, HttpUrl
from typing import Annotated, Optional
from app.schemas.RealUser import ReducedUser
from datetime import datetime

PhotoUrl = Annotated[HttpUrl, AfterValidator(lambda v: str(v))]

TagType = Annotated[str, Field(..., min_length=2,
                               max_length=128,
                               pattern=r"^[a-zA-Z0-9_]*$")]


class PostCommentSchema(BaseModel):
    id: str = Field(...)
    author: int = Field(..., example=1)
    content: str = Field(..., max_length=512)
    created_at: datetime


class CreatePostCommentSchema(BaseModel):
    body: str


class DeletePostCommentSchema(BaseModel):
    comment_id: str


class PostCreateSchema(BaseModel):
    author_user_id: int = Field(..., example=1)
    content: str = Field(..., max_length=512)
    tags: Optional[list[TagType]] = None
    photo_links: Optional[list[PhotoUrl]] = None
    comments: list[PostCommentSchema] = []

    class Config:
        json_schema_extra = {
            "example": {
                "author_user_id": 17,
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
                "comments": [],
                "comments_count": 0
            }
        }


class PostBaseModel(BaseModel):
    id: str = Field(...)
    author: ReducedUser = Field(...)
    content: str = Field(..., max_length=512)
    likes_count: int = Field(default=0)
    created_at: datetime
    updated_at: datetime
    tags: Optional[list[TagType]] = None
    comments: list[PostCommentSchema] = []
    comments_count: int = Field(default=0)


class PostSchema(PostBaseModel):
    photo_links: Optional[list[PhotoUrl]] = None

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "author": 17,
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
                "comments": [{
                    "id": "fdfe6218-64f7-4f89-af36-42b8b035f4c8",
                    "author": 11,
                    "content": "bien ahi!!",
                    "created_at": "2024-04-16T05:35:30.127Z"
                }],
                "comments_count": 1
            }
        }


class PostInFeedSchema(PostBaseModel):
    main_photo_link: Optional[PhotoUrl] = None

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "author_user_id": 17,
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
                "comments": [],
                "comments_count": 0
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
    comments: Optional[list[PostCommentSchema]] = None
    comments_count: Optional[int] = None

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
                ]
            }
        }


class GetPostCommentSchema(BaseModel):
    id: str = Field(...)
    author: ReducedUser = Field(...)
    content: str = Field(..., max_length=512)
    created_at: datetime


class GetPostSchema(BaseModel):
    id: str = Field(...)
    author: ReducedUser = Field(...)
    content: str = Field(..., max_length=512)
    photo_links: Optional[list[PhotoUrl]] = None
    likes_count: int = Field(default=0)
    created_at: datetime
    updated_at: datetime
    tags: Optional[list[TagType]] = None
    comments: list[GetPostCommentSchema] = []
    comments_count: int = Field(default=0)


class PostPagination(BaseModel):
    time_offset: datetime
    page: int
    per_page: int


class PostFilters(BaseModel):
    pagination: PostPagination
    users: Optional[list[int]] = None
    tags: Optional[str] = Field(..., min_length=2, max_length=128)
