from datetime import datetime
import logging
import uuid
from typing import List, Optional
from app.models.Post import Post
from app.repository.SocialRepository import SocialRepository
from app.service.Users import UserService
from app.schemas.Post import (
    GetPostCommentSchema,
    GetPostSchema,
    PostCommentSchema,
    PostCreateSchema,
    PostFilters,
    PostInFeedSchema,
    PostPagination,
    PostSchema,
    PostPartialUpdateSchema,
)
from app.exceptions.NotFoundException import ItemNotFound
from app.schemas.SocialUser import (
    SocialUserCreateSchema,
    UserPartialUpdateSchema,
    SocialUserSchema,
    UserSchema,
)
from app.exceptions.BadRequestException import BadRequestException
from app.models.SocialUser import SocialUser
from app.schemas.RealUser import GetUserSchema, ReducedUser

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
        created_post = self.social_repository.get_post(id_post)
        print("created: ", created_post)
        map_author_user_id(user, created_post)
        print("created w user: ", created_post)
        return PostSchema.model_validate(created_post)

    async def get_post(self, id_post: int) -> PostSchema:
        post: Post = self.social_repository.get_post(id_post)
        if post is None:
            raise ItemNotFound("Post", id_post)

        get_user: GetUserSchema = await UserService.get_user(post["author_user_id"])
        user: ReducedUser = ReducedUser.from_pydantic(get_user)
        map_author_user_id(user, post)

        final_comments = []

        for comment in post['comments']:
            get_user: GetUserSchema = await UserService.get_user(comment['author'])
            author: ReducedUser = ReducedUser.from_pydantic(get_user)
            valid_comment = GetPostCommentSchema(id=comment['id'],
                                                 author=author,
                                                 content=comment['content'],
                                                 created_at=comment['created_at']
                                                 )
            final_comments.append(valid_comment)

        return GetPostSchema(
                    id=post['id'],
                    author=user,
                    content=post['content'],
                    likes_count=post['likes_count'],
                    created_at=post['created_at'],
                    updated_at=post['updated_at'],
                    tags=post['tags'],
                    comments=final_comments,
                    comments_count=post['comments_count']
                )

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

    async def get_social_user(self, id_user: int) -> UserSchema:
        social_user = self.social_repository.get_social_user(id_user)
        get_user: GetUserSchema = await UserService.get_user(id_user)
        user = {'_id': id_user,
                'following': social_user["following"],
                'followers': social_user["followers"],
                'tags': social_user["tags"],
                'name': get_user.name,
                'photo': get_user.photo,
                'nickname': get_user.nickname
                }
        return UserSchema.model_validate(user)

    async def _update_social_user(
        self,
        id_user: str,
        update_user_set: UserPartialUpdateSchema,
    ) -> Optional[SocialUserSchema]:
        update_user_obj = UserPartialUpdateSchema.parse_obj(update_user_set)
        self.social_repository.update_user(
            id_user,
            update_user_obj.model_dump_json(exclude_none=True)
        )
        return await self.get_social_user(id_user)

    async def get_my_feed(
        self, user_id: int, pagination: PostPagination
    ) -> List[PostInFeedSchema]:
        following = self.social_repository.get_following_of(user_id)
        following.append(user_id)  # Add the user itself to the feed!
        filters = PostFilters(pagination=pagination, users=following, tags=None)
        print(f"[FILTERS]: {filters}")
        return await self._get_all(filters)

    async def _get_all(self, filters: PostFilters) -> List[PostSchema]:
        cursor = self.social_repository.get_posts_by(filters)
        fetched_posts = []
        users_ids_to_fetch = set()

        for post in cursor:
            author_id = post["author_user_id"]
            users_ids_to_fetch.add(author_id)
            fetched_posts.append(post)

        if fetched_posts == []:
            return []

        users_fetched_hash = {}
        users_fetched_list = await UserService.get_users(list(users_ids_to_fetch))

        for user in users_fetched_list:
            users_fetched_hash[user.id] = user

        final_posts = []

        for post in fetched_posts:
            author_id = post["author_user_id"]
            get_user: GetUserSchema = await UserService.get_user(author_id)
            user: ReducedUser = ReducedUser.from_pydantic(get_user)
            map_author_user_id(user, post)
            valid_post = PostInFeedSchema.from_post(PostSchema.model_validate(post))
            final_posts.append(valid_post)

        return final_posts

    async def follow_social_user(self, user_id, user_to_follow_id):
        if (user_id == user_to_follow_id):
            raise BadRequestException("Must follow another user")
        following = self.social_repository.get_following_of(user_id)
        if not await UserService.user_exists(user_to_follow_id):
            raise BadRequestException("User does not exist in the system!")
        if user_to_follow_id in following:
            return
        following.append(user_to_follow_id)
        updates: UserPartialUpdateSchema = {"following":
                                            [user_id for user_id in following]}
        await self._update_social_user(user_id, updates)

        followers = self.social_repository.get_followers_of(user_to_follow_id)
        followers.append(user_id)
        updates: UserPartialUpdateSchema = {"followers":
                                            [user_id for user_id in followers]}
        await self._update_social_user(user_to_follow_id, updates)

    async def unfollow_social_user(self, user_id, user_to_unfollow_id):
        if (user_id == user_to_unfollow_id):
            raise BadRequestException("Must unfollow another user")
        following = self.social_repository.get_following_of(user_id)
        if not await UserService.user_exists(user_to_unfollow_id):
            raise BadRequestException("User does not exist in the system!")
        if user_to_unfollow_id not in following:
            return
        following.remove(user_to_unfollow_id)
        updates: UserPartialUpdateSchema = {"following":
                                            [user_id for user_id in following]}
        await self._update_social_user(user_id, updates)

        followers = self.social_repository.get_followers_of(user_to_unfollow_id)
        if user_id not in followers:
            return
        followers.remove(user_id)
        updates: UserPartialUpdateSchema = {"followers":
                                            [user_id for user_id in followers]}
        await self._update_social_user(user_to_unfollow_id, updates)

    async def comment_post(self, post_id, author_id, comment_body) -> PostCommentSchema:
        post: Post = self.social_repository.get_post(post_id)
        if post is None:
            raise ItemNotFound("Post", post_id)

        comment: PostCommentSchema = {
            "id": str(uuid.uuid4()),
            "author": author_id,
            "content": comment_body,
            "created_at": datetime.now()
        }
        comments = post["comments"]
        comments.append(comment)
        comments_count = post["comments_count"] + 1
        updates = PostPartialUpdateSchema(comments=comments,
                                          comments_count=comments_count)
        await self.update_post(post_id, updates)
        return PostCommentSchema.model_validate(comment)

    async def delete_post_comment(self, post_id, comment_id) -> str:
        post: Post = self.social_repository.get_post(post_id)
        if post is None:
            raise ItemNotFound("Post", post_id)

        comment = find_comment_by_id(post, comment_id)

        if comment is None:
            return None

        comments = post["comments"]
        for comment in comments:
            if comment["id"] == comment_id:
                comments.remove(comment)

        comments_count = post["comments_count"] - 1
        updates = PostPartialUpdateSchema(comments=comments,
                                          comments_count=comments_count)
        await self.update_post(post_id, updates)
        return comment_id


def find_comment_by_id(post: Post, comment_id: str) -> Optional[PostCommentSchema]:
    for comment in post["comments"]:
        if comment["id"] == comment_id:
            return comment
    return None


def map_author_user_id(user, created_post):
    created_post["author"] = user
    created_post.pop("author_user_id")
