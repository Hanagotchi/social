import logging
from httpx import AsyncClient, HTTPStatusError, Response, AsyncHTTPTransport
from os import environ
from app.exceptions.InternalServerErrorException import InternalServerErrorException
from app.exceptions.NotFoundException import ItemNotFound
from app.schemas.RealUser import GetUserSchema

logger = logging.getLogger("users")
logger.setLevel("DEBUG")

USERS_SERVICE_URL = environ["USERS_SERVICE_URL"]

# Heroku dyno plan has a limit of 30 seconds...
# so, assign 3 retries of 10 seconds each :)
# https://devcenter.heroku.com/articles/request-timeout
NUMBER_OF_RETRIES = 3
TIMEOUT = 10


class UserService:
    @staticmethod
    async def get(path: str) -> Response:
        async with AsyncClient(
            transport=AsyncHTTPTransport(retries=NUMBER_OF_RETRIES), timeout=TIMEOUT
        ) as client:
            response = await client.get(USERS_SERVICE_URL + path)
            return response

    @staticmethod
    async def get_user(author_user_id: int) -> GetUserSchema:
        try:
            response = await UserService.get(f"/users/{author_user_id}")
            if response.status_code == 200:
                user = response.json()["message"]
                return GetUserSchema(**user)
            else:
                raise ItemNotFound("User", author_user_id)
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ItemNotFound("User", author_user_id)
            else:
                print(f"HTTPStatusError error: {e}")
                raise InternalServerErrorException("User service")
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise InternalServerErrorException("User service")

    @staticmethod
    async def get_users(query_params: dict) -> list:
        try:
            query_string = '&'.join([f"{k}={v}" for k, v in query_params.items() if v])
            path = f"/users?{query_string}"
            response = await UserService.get(path)
            if response.status_code == 200:
                users = response.json()["message"]
                return [GetUserSchema(**user) for user in users]
            elif response.status_code == 204:
                return []
            else:
                raise InternalServerErrorException("User service")
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise InternalServerErrorException("User service")

    @staticmethod
    async def user_exists(user_id: int) -> bool:
        try:
            response = await UserService.get(f"/users/{user_id}")
            return response.status_code == 200
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            else:
                print(f"HTTPStatusError error: {e}")
                raise InternalServerErrorException("User service")
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise InternalServerErrorException("User service")
