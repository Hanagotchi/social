from typing import Annotated
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, Depends, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel

SECRET_KEY = "secret"
ALGORITHM = "HS256"
TOKEN_FIELD_NAME = "x-access-token"


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        try:
            credentials: HTTPAuthorizationCredentials = await super().__call__(request)
            if credentials.scheme != "Bearer" or not self.verify_jwt(
                credentials.credentials
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme or token.",
                )
            return credentials.credentials

        except Exception:
            access_token = request.headers.get(TOKEN_FIELD_NAME)
            if access_token and self.verify_jwt(access_token):
                return access_token

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization code or token.",
            )

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = jwt.decode(jwtoken, SECRET_KEY, algorithms=ALGORITHM)
        except Exception:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid


class TokenData(BaseModel):
    user_id: int | None = None


async def get_current_user_id(token: Annotated[dict, Depends(JWTBearer())]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    return token_data.user_id
