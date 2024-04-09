from typing import Optional
from app.schemas.Post import (
    PostCreateSchema,
    PostPartialUpdateSchema,
    PostSchema,
)
from app.service.Social import SocialService
from fastapi import HTTPException, status, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class SocialController:

    def __init__(self, social_service: SocialService):
        self.social_service = social_service

    async def handle_create_post(
        self, input_post: PostCreateSchema
    ) -> JSONResponse:
        post: PostSchema = await self.social_service.create_post(
            input_post
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content=jsonable_encoder(post)
        )

    def handle_get_post(self, id_post: str) -> JSONResponse:
        post: PostSchema = self.social_service.get_post(
            id_post
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(post)
        )

    def handle_update_post(
        self,
        id_post: str,
        post_update_set: PostPartialUpdateSchema,
    ) -> JSONResponse:
        post: Optional[PostSchema] = (
            self.social_service.update_post(
                id_post, post_update_set
            )
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
