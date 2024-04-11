from fastapi import HTTPException, status
from typing import Optional


class BadRequestException(HTTPException):
    def __init__(
        self,
        detail: Optional[str] = None,
    ):
        status_code = status.HTTP_400_BAD_REQUEST
        message = "Bad request"
        if detail:
            message += f": {detail.lower()}"

        super().__init__(status_code=status_code, detail=message)
