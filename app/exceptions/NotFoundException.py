from fastapi import HTTPException, status
from typing import Optional


class NotFoundException(HTTPException):
    def __init__(
        self,
        detail: Optional[str] = None,
    ):
        status_code = status.HTTP_404_NOT_FOUND
        message = "Item not found"
        if detail:
            message += f": {detail.lower()}"
        super().__init__(status_code=status_code, detail=message)


class ItemNotFound(HTTPException):
    def __init__(self, item: str, id):
        status_code = status.HTTP_404_NOT_FOUND
        message = f"{item} with id {id} not found"
        super().__init__(status_code=status_code, detail=message)
