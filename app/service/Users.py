import logging
from httpx import AsyncClient, HTTPStatusError, Response
from os import environ
from app.exceptions.InternalServerErrorException import InternalServerErrorException
from app.exceptions.NotFoundException import ItemNotFound

logger = logging.getLogger("users")
logger.setLevel("DEBUG")

USERS_SERVICE_URL = environ["USERS_SERVICE_URL"]


class UserService:
    @staticmethod
    async def get(path: str) -> Response:
        async with AsyncClient() as client:
            response = await client.get(USERS_SERVICE_URL + path)
            return response.raise_for_status()

    @staticmethod
    async def check_existing_user(author_user_id: int) -> Response:
        try:
            response = await UserService.get(f"/users/{author_user_id}")
            if response.status_code == 200:
                return
            else:
                raise ItemNotFound("User", author_user_id)
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ItemNotFound("User", author_user_id)
            else:
                raise InternalServerErrorException("User service")
        except Exception:
            raise InternalServerErrorException("User service")
