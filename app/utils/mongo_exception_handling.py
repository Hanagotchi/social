from app.exceptions.BadRequestException import BadRequestException
from bson.errors import InvalidId
import logging

logger = logging.getLogger("app")
logger.setLevel("DEBUG")


def handle_common_errors(err):
    logger.error(format(err))
    if isinstance(err, InvalidId):
        raise BadRequestException(
            detail=f"Invalid ID. {err}",
        )
    # if isinstance(err, IntegrityError):
    #     if isinstance(err.orig, UniqueViolation):
    #         parsed_error = err.orig.pgerror.split("\n")
    #         raise BadRequestException(
    #             detail="Unique Violation: "
    #             + f"{parsed_error[0]}. More detail: {parsed_error[1]}"
    #         )

    #     raise InternalServerErrorException(
    #         detail=format(err),
    #     )

    # if isinstance(err, PendingRollbackError):
    #     raise InternalServerErrorException(
    #         detail=format(err),
    #     )

    # if isinstance(err, NoResultFound):
    #     raise NotFoundException(
    #         detail=format(err),
    #     )

    # raise InternalServerErrorException(
    #     detail=format(err),
    # )
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
