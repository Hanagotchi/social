import logging
from app.models.Publication import Publication
from app.repository.SocialRepository import SocialRepository
from app.service.Users import UserService
from app.schemas.Publication import (
    PublicationCreateSchema,
    PublicationSchema,
)
from app.exceptions.NotFoundException import ItemNotFound

logger = logging.getLogger("app")
logger.setLevel("DEBUG")


class SocialService:

    def __init__(self, social_repository: SocialRepository):
        self.social_repository = social_repository

    async def post_publication(
        self, input_publication: PublicationCreateSchema
    ) -> PublicationSchema:
        await UserService.check_existing_user(input_publication.author_user_id)
        try:
            publication = Publication.from_pydantic(input_publication)
            id_publication = self.social_repository.post_publication(publication)
            crated_publication: Publication = self.social_repository.get_publication(
                id_publication
            )
            return PublicationSchema.model_validate(crated_publication)
        except Exception as err:
            self.social_repository.rollback()
            raise err

    def get_publication(self, id_publication: int) -> PublicationSchema:
        publication: Publication = self.social_repository.get_publication(
            id_publication
        )
        if publication is None:
            raise ItemNotFound("Publication", id_publication)
        return PublicationSchema.model_validate(publication)
