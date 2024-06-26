from datetime import datetime
from functools import wraps
import logging
from bson import ObjectId

logger = logging.getLogger("app")
logger.setLevel("DEBUG")


def updatedAtTrigger(collection_name: str):
    """
    Decorator to update the updated_at field of a document
    in the database when a function is called and returns 1 (success update).
    Args:
        collection_name (str): name of the collection to update the updated_at field
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if result and result == 1:
                id_post = args[1]

                collection = (
                    args[0].posts_collection
                    if collection_name == "posts"
                    else args[0].users_collection
                )
                collection.update_one(
                    {"_id": ObjectId(id_post)},
                    {"$set": {"updated_at": datetime.now()}},
                )

            return result

        return wrapper

    return decorator
