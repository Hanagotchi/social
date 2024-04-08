from app.schemas.Publication import (
    PublicationCreateSchema,
    PublicationSchema,
)
from app.service.Social import SocialService
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class SocialController:

    def __init__(self, social_service: SocialService):
        self.social_service = social_service

    async def handle_create_publication(
        self, input_publication: PublicationCreateSchema
    ) -> JSONResponse:
        publication: PublicationSchema = await self.social_service.create_publication(
            input_publication
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content=jsonable_encoder(publication)
        )

    def handle_get_publication(self, id_publication: str) -> JSONResponse:
        publication: PublicationSchema = self.social_service.get_publication(
            id_publication
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(publication)
        )
