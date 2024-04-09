import logging
from app.models.Post import Post
from app.repository.SocialRepository import SocialRepository
from app.service.Users import UserService
from app.schemas.Post import (
    PostCreateSchema,
    PostSchema,
)
from app.exceptions.NotFoundException import ItemNotFound

logger = logging.getLogger("app")
logger.setLevel("DEBUG")


class SocialService:

    def __init__(self, social_repository: SocialRepository):
        self.social_repository = social_repository

    async def create_post(self, input_post: PostCreateSchema) -> PostSchema:
        await UserService.check_existing_user(input_post.author_user_id)
        try:
            post = Post.from_pydantic(input_post)
            id_post = self.social_repository.add_post(post)
            crated_post: Post = self.social_repository.get_post(id_post)
            return PostSchema.model_validate(crated_post)
        except Exception as err:
            self.social_repository.rollback()
            raise err

    def get_post(self, id_post: int) -> PostSchema:
        post: Post = self.social_repository.get_post(id_post)
        if post is None:
            raise ItemNotFound("Post", id_post)
        return PostSchema.model_validate(post)
