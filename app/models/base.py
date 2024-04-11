from typing import Annotated
from pydantic import BaseModel, BeforeValidator


class Base(BaseModel):
    __collectionname__: str
    pass


PyObjectId = Annotated[str, BeforeValidator(str)]
