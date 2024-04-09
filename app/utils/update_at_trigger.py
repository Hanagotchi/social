from datetime import datetime
from functools import wraps
import logging
from zoneinfo import ZoneInfo
from bson import ObjectId

logger = logging.getLogger("app")
logger.setLevel("DEBUG")


def updateAtTrigger():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if result and result == 1:
                id_publication = args[1]
                args[0].publications_collection.update_one(
                    {"_id": ObjectId(id_publication)},
                    {
                        "$set": {
                            "updated_at": datetime.now(
                                ZoneInfo("America/Argentina/Buenos_Aires")
                            ).isoformat()[:-6]
                        }
                    },
                )

            return result

        return wrapper

    return decorator
