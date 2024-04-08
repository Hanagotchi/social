from typing import Optional
from app.schemas.Publication import (
    PublicationCreateSchema,
    PublicationPartialUpdateSchema,
    PublicationSchema,
)
from app.service.Social import SocialService
from fastapi import HTTPException, status, Response
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

    def handle_update_publication(
        self,
        id_publication: str,
        publication_update_set: PublicationPartialUpdateSchema,
    ) -> JSONResponse:
        publication: Optional[PublicationSchema] = (
            self.social_service.update_publication(
                id_publication, publication_update_set
            )
        )

        if publication:
            return JSONResponse(
                status_code=status.HTTP_200_OK, content=jsonable_encoder(publication)
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not found a publication with id {id_publication}",
        )

    def handle_delete_publication(self, id_publication: str) -> JSONResponse:
        row_count = self.social_service.delete_publication(id_publication)
        if row_count == 0:
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content="Publication deleted successfully",
        )
