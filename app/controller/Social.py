from typing import Optional
from app.schemas.Post import (
    PostCommentSchema,
    PostCreateSchema,
    PostFilters,
    PostPagination,
    PostPartialUpdateSchema,
    PostSchema,
)
from app.service.Social import SocialService
from fastapi import HTTPException, status, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.schemas.SocialUser import (
    SocialUserCreateSchema,
    SocialUserSchema,
    TagSchema,
    UserSchema
)


class SocialController:

    def __init__(self, social_service: SocialService):
        self.social_service = social_service

    async def handle_create_post(self, input_post: PostCreateSchema) -> JSONResponse:
        post: PostSchema = await self.social_service.create_post(input_post)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content=jsonable_encoder(post)
        )

    async def handle_get_post(self, requestor_id: int, id_post: str) -> JSONResponse:
        post: PostSchema = await self.social_service.get_post(
            id_post, requestor_id
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(post)
        )

    async def handle_update_post(
        self,
        user_id: int,
        id_post: str,
        update_post_set: PostPartialUpdateSchema,
    ) -> JSONResponse:
        post: Optional[PostSchema] = await self.social_service.update_post(
            user_id, id_post, update_post_set
        )

        if post:
            return JSONResponse(
                status_code=status.HTTP_200_OK, content=jsonable_encoder(post)
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not found a post with id {id_post}",
        )

    def handle_delete_post(self, id_post: str) -> JSONResponse:
        row_count = self.social_service.delete_post(id_post)
        if row_count == 0:
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content="Post deleted successfully",
        )

    async def handle_get_my_feed(
        self, user_id: int, pagination: PostPagination
    ) -> JSONResponse:
        list = await self.social_service.get_my_feed(user_id, pagination)
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(list)
        )

    async def handle_create_social_user(
        self, input_user: SocialUserCreateSchema
    ) -> JSONResponse:
        user: SocialUserSchema = await self.social_service.create_social_user(
            input_user
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content=jsonable_encoder(user)
        )

    async def handle_get_all(
            self, requestor_id: int, filters: PostFilters) -> JSONResponse:
        list = await self.social_service._get_all(filters, requestor_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(list)
        )

    async def handle_get_social_user(self, user_id: int) -> JSONResponse:
        user: UserSchema = await self.social_service.get_social_user(user_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(user)
        )

    async def handle_follow_social_user(
        self,
        user_id: str,
        user_to_follow_id: str,
    ) -> JSONResponse:

        await self.social_service.follow_social_user(user_id, user_to_follow_id)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content="User followed successfully")

    async def handle_unfollow_social_user(
        self,
        user_id: str,
        user_to_unfollow_id: str,
    ) -> JSONResponse:

        await self.social_service.unfollow_social_user(user_id, user_to_unfollow_id)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content="User unfollowed successfully")

    async def handle_subscribe_to_tag(
        self,
        user_id: str,
        tag: TagSchema,
    ) -> JSONResponse:

        result = await self.social_service.subscribe_to_tag(user_id, tag)
        if result is None:
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content="Tag subscribed successfully")

    async def handle_unsubscribe_to_tag(
        self,
        user_id: str,
        tag: TagSchema,
    ) -> JSONResponse:

        result = await self.social_service.unsubscribe_to_tag(user_id, tag)
        if result is None:
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content="Tag unsubscribed successfully")

    async def handle_like_post(
        self,
        user_id: int,
        post_id: str,
    ) -> JSONResponse:
        result = await self.social_service.like_post(user_id, post_id)
        if result is None or result == 0:
            return JSONResponse(
                status_code=status.HTTP_204_NO_CONTENT,
                content=""
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content="Post liked successfully"
        )

    async def handle_unlike_post(
        self,
        user_id: int,
        post_id: str,
    ) -> JSONResponse:
        result = await self.social_service.unlike_post(user_id, post_id)

        if result is None or result == 0:
            return JSONResponse(
                status_code=status.HTTP_204_NO_CONTENT,
                content=""
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content="Post unliked successfully"
        )

    async def handle_comment_post(
        self,
        post_id: str,
        user_id: str,
        comment: str,
    ) -> JSONResponse:

        comment: PostCommentSchema = await self.social_service.comment_post(
            post_id,
            user_id,
            comment
        )

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=jsonable_encoder(comment))

    async def handle_delete_post_comment(
        self,
        user_id: int,
        post_id: str,
        comment_id: str,
    ) -> JSONResponse:

        response = await self.social_service.delete_post_comment(user_id, post_id, comment_id)

        if (response is None):
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content="Comment deleted successfully")

    async def handle_get_user_followers(self, query_params: dict) -> JSONResponse:
        followers = await self.social_service.get_user_followers(query_params)
        if followers:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(followers)
            )
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=jsonable_encoder(followers)
        )
