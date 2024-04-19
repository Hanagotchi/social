import logging
from typing import List, Optional
from app.models.Post import Post
from app.repository.SocialRepository import SocialRepository
from app.service.Users import UserService
from app.schemas.Post import (
    PostCreateSchema,
    PostFilters,
    PostInFeedSchema,
    PostPagination,
    PostSchema,
    PostPartialUpdateSchema,
)
from app.exceptions.NotFoundException import ItemNotFound
from app.schemas.RealUser import GetUserSchema, ReducedUser
from app.schemas.SocialUser import SocialUserCreateSchema, SocialUserSchema
from app.models.SocialUser import SocialUser
from app.exceptions.BadRequestException import BadRequestException

logger = logging.getLogger("app")
logger.setLevel("DEBUG")


class SocialService:

    def __init__(self, social_repository: SocialRepository):
        self.social_repository = social_repository

    async def create_post(self, input_post: PostCreateSchema) -> PostSchema:
        get_user: GetUserSchema = await UserService.get_user(input_post.author_user_id)
        user: ReducedUser = ReducedUser.from_pydantic(get_user)
        post = Post.from_pydantic(input_post)
        id_post = self.social_repository.add_post(post)
        crated_post = self.social_repository.get_post(id_post)
        map_author_user_id(user, crated_post)
        return PostSchema.model_validate(crated_post)

    async def get_post(self, id_post: int) -> PostSchema:
        post: Post = self.social_repository.get_post(id_post)
        if post is None:
            raise ItemNotFound("Post", id_post)
        get_user: GetUserSchema = await UserService.get_user(post["author_user_id"])
        user: ReducedUser = ReducedUser.from_pydantic(get_user)
        map_author_user_id(user, post)
        return PostSchema.model_validate(post)

    async def update_post(
        self,
        id_post: str,
        update_post_set: PostPartialUpdateSchema,
    ) -> Optional[PostSchema]:
        self.social_repository.update_post(
            id_post, update_post_set.model_dump_json(exclude_none=True)
        )
        return await self.get_post(id_post)

    def delete_post(self, id_post: str):
        row_count = self.social_repository.delete_post(id_post)
        return row_count

    async def create_social_user(
        self, input_user: SocialUserCreateSchema
    ) -> SocialUserSchema:
        if not await UserService.user_exists(input_user.id):
            raise BadRequestException("User does not exist in the system!")

        user = SocialUser.from_pydantic(input_user)
        user_id = self.social_repository.add_social_user(user)
        crated_user = self.social_repository.get_social_user(user_id)

        return SocialUserSchema.model_validate(crated_user)

    async def get_my_feed(
        self, user_id: int, pagination: PostPagination
    ) -> List[PostInFeedSchema]:
        following = self.social_repository.get_following_of(user_id)
        following.append(user_id)  # Add the user itself to the feed!
        filters = PostFilters(pagination=pagination, users=following, tags=None)
        print(f"[FILTERS]: {filters}")
        return await self.get_all(user_id, filters)

    async def get_all(self, user_id: int, filters: PostFilters) -> List[PostSchema]:
        cursor = self.social_repository.get_posts_by(filters)
        fetched_posts = []
        users_ids_to_fetch = set()

        for post in cursor:
            author_id = post["author_user_id"]
            users_ids_to_fetch.add(author_id)
            fetched_posts.append(post)

        users_fetched_hash = {}
        users_fetched_list = await UserService.get_users(list(users_ids_to_fetch))

        for user in users_fetched_list:
            users_fetched_hash[user.id] = user

        final_posts = []

        for post in fetched_posts:
            author_id = post["author_user_id"]
            get_user: GetUserSchema = users_fetched_hash.get(author_id)
            user: ReducedUser = ReducedUser.from_pydantic(get_user)
            map_author_user_id(user, post)
            valid_post = PostInFeedSchema.from_post(PostSchema.model_validate(post))
            final_posts.append(valid_post)

        return final_posts


def map_author_user_id(user, post):
    post["author"] = user
    post.pop("author_user_id")
