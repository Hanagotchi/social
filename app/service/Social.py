import logging
from typing import Optional
import re

from app.models.Post import Post
from app.repository.SocialRepository import SocialRepository
from app.service.Users import UserService
from app.schemas.Post import (
    PostCreateSchema,
    PostSchema,
    PostPartialUpdateSchema,
)
from app.exceptions.NotFoundException import ItemNotFound
from app.exceptions import BadRequestException
from app.schemas.User import GetUserSchema, User

logger = logging.getLogger("app")
logger.setLevel("DEBUG")


class SocialService:

    def __init__(self, social_repository: SocialRepository):
        self.social_repository = social_repository

    async def create_post(self, input_post: PostCreateSchema) -> PostSchema:
        check_valid_photo_links(input_post)
        get_user: GetUserSchema = await UserService.get_user(input_post.author_user_id)
        user: User = User.from_pydantic(get_user)
        try:
            post = Post.from_pydantic(input_post)
            id_post = self.social_repository.add_post(post)
            crated_post = self.social_repository.get_post(id_post)
            map_author_user_id(user, crated_post)
            return PostSchema.model_validate(crated_post)
        except Exception as err:
            self.social_repository.rollback()
            raise err

    async def get_post(self, id_post: int) -> PostSchema:
        post: Post = self.social_repository.get_post(id_post)
        if post is None:
            raise ItemNotFound("Post", id_post)
        get_user: GetUserSchema = await UserService.get_user(post["author_user_id"])
        user: User = User.from_pydantic(get_user)
        map_author_user_id(user, post)
        return PostSchema.model_validate(post)

    def update_post(
        self,
        id_post: str,
        post_update_set: PostPartialUpdateSchema,
    ) -> Optional[PostSchema]:
        try:
            self.social_repository.update_post(
                id_post, post_update_set.content
            )
            updated_post = self.social_repository.get_post(id_post)
            return PostSchema.model_validate(updated_post)
        except Exception as err:
            raise err

    def delete_post(self, id_post: str):
        try:
            row_count = self.social_repository.delete_post(id_post)
            return row_count
        except Exception as err:
            raise err
   

def check_valid_photo_links(input_post):
    if input_post.photo_links:
        for photo_link in input_post.photo_links:
            if not re.match(
                r"^https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}"
                r"(?:/[^/#?]+)+(?:\?.*)?$",
                photo_link,
            ):
                raise BadRequestException("Invalid photo URL")


def map_author_user_id(user, crated_post):
    crated_post["author"] = user
    crated_post.pop("author_user_id")
