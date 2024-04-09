import logging
from app.exceptions.BadRequestException import BadRequestException
from bson.errors import BSONError, InvalidId
from pymongo.errors import PyMongoError
from app.exceptions import InternalServerErrorException

logger = logging.getLogger("app")
logger.setLevel("DEBUG")


def handle_common_errors(err):
    logger.error(format(err))
    if isinstance(err, BSONError):
        if isinstance(err, InvalidId):
            raise BadRequestException(
                detail=f"Invalid ID. {err}",
            )

        raise InternalServerErrorException(
            detail=f"Error in BSON: {err}",
        )

    if isinstance(err, PyMongoError):
        raise InternalServerErrorException(
            detail=f"Error in MongoDB: {err}",
        )

    raise err


def withMongoExceptionsHandle(async_mode: bool = False):
    def decorator(func):
        async def handleAsyncMongoException(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as err:
                return handle_common_errors(err)

        def handleSyncMongoException(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as err:
                return handle_common_errors(err)

        return handleAsyncMongoException if async_mode else handleSyncMongoException

    return decorator
