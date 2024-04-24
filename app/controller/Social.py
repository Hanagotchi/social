from typing import Optional
from app.schemas.Post import (
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
from app.schemas.SocialUser import SocialUserCreateSchema, SocialUserSchema, UserSchema


class SocialController:

    def __init__(self, social_service: SocialService):
        self.social_service = social_service

    async def handle_create_post(self, input_post: PostCreateSchema) -> JSONResponse:
        post: PostSchema = await self.social_service.create_post(input_post)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content=jsonable_encoder(post)
        )

    async def handle_get_post(self, id_post: str) -> JSONResponse:
        post: PostSchema = await self.social_service.get_post(id_post)
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(post)
        )

    async def handle_update_post(
        self,
        id_post: str,
        update_post_set: PostPartialUpdateSchema,
    ) -> JSONResponse:
        post: Optional[PostSchema] = await self.social_service.update_post(
            id_post, update_post_set
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

    async def handle_get_all(self, filters: PostFilters) -> JSONResponse:
        list = await self.social_service.get_all(filters)
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
