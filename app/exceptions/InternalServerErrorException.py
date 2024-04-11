from fastapi import HTTPException, status
from typing import Optional


class InternalServerErrorException(HTTPException):
    def __init__(
        self,
        microservice: Optional[str] = "Social service",
        detail: Optional[str] = None,
    ):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = f"An error occurred in the {microservice}"

        if detail:
            message += f": {detail.lower()}"

        super().__init__(status_code=status_code, detail=message)
