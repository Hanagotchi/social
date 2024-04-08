import logging
from typing import Optional
from app.models.Publication import Publication
from app.repository.SocialRepository import SocialRepository
from app.service.Users import UserService
from app.schemas.Publication import (
    PublicationCreateSchema,
    PublicationSchema,
    PublicationPartialUpdateSchema,
)
from app.exceptions.NotFoundException import ItemNotFound

logger = logging.getLogger("app")
logger.setLevel("DEBUG")


class SocialService:

    def __init__(self, social_repository: SocialRepository):
        self.social_repository = social_repository

    async def create_publication(
        self, input_publication: PublicationCreateSchema
    ) -> PublicationSchema:
        await UserService.check_existing_user(input_publication.id_user)
        try:
            publication = Publication.from_pydantic(input_publication)
            id_publication = self.social_repository.add_publication(publication)
            crated_publication: Publication = self.social_repository.get_publication(
                id_publication
            )
            return PublicationSchema.model_validate(crated_publication)
        except Exception as err:
            print(err)
            self.social_repository.rollback()
            raise err

    def get_publication(self, id_publication: int) -> PublicationSchema:
        publication: Publication = self.social_repository.get_publication(
            id_publication
        )
        print(publication)
        if publication is None:
            raise ItemNotFound("Publication", id_publication)
        return PublicationSchema.model_validate(publication)

    def update_publication(
        self,
        id_publication: str,
        publication_update_set: PublicationPartialUpdateSchema,
    ) -> Optional[PublicationSchema]:
        try:
            self.social_repository.update_publication(
                id_publication, publication_update_set.content
            )
            updated_publication = self.social_repository.get_publication(id_publication)
            return PublicationSchema.model_validate(updated_publication)
        except Exception as err:
            self.social_repository.rollback()
            raise err

    def delete_publication(self, id_publication: str):
        try:
            row_count = self.social_repository.delete_publication(id_publication)
            return row_count
        except Exception as err:
            self.social_repository.rollback()
            raise err
