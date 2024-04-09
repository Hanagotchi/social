from app.schemas.Post import (
    PostCreateSchema,
    PostSchema,
)
from app.service.Social import SocialService
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class SocialController:

    def __init__(self, social_service: SocialService):
        self.social_service = social_service

    async def handle_create_post(self, input_post: PostCreateSchema) -> JSONResponse:
        post: PostSchema = await self.social_service.create_post(input_post)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content=jsonable_encoder(post)
        )

    def handle_get_post(self, id_post: str) -> JSONResponse:
        post: PostSchema = self.social_service.get_post(id_post)
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(post)
        )
