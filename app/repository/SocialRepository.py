from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.base import Base
from app.schemas.Post import PostFilters


class SocialRepository(ABC):

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def add_post(self, record: Base) -> Optional[str]:
        pass

    @abstractmethod
    def get_post(self, id_received: int) -> Base:
        pass

    @abstractmethod
    def get_posts_by(self, filters: PostFilters) -> List[Base]:
        pass

    @abstractmethod
    def update_post(
        self,
        id_post: str,
        update_post_set: str,
    ) -> Optional[int]:
        pass

    @abstractmethod
    def delete_post(self, id_received: str) -> int:
        pass
