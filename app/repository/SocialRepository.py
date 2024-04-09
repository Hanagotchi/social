from abc import ABC, abstractmethod
from typing import Optional
from app.models.base import Base


class SocialRepository(ABC):

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def post_publication(self, record: Base) -> Optional[str]:
        pass

    @abstractmethod
    def get_publication(self, id_received: int) -> Base:
        pass

    @abstractmethod
    def update_publication(
        self,
        id_publication: str,
        content: Optional[str],
    ):
        pass

    @abstractmethod
    def delete_publication(self, id_received: str) -> int:
        pass
