from datetime import datetime
import json
from zoneinfo import ZoneInfo
from bson import ObjectId
import pymongo
from dotenv import load_dotenv
from os import environ
from app.models.base import Base
from app.models.Post import Post
from typing import Optional
from app.repository.SocialRepository import SocialRepository
from app.exceptions.NotFoundException import ItemNotFound
from app.utils.mongo_exception_handling import withMongoExceptionsHandle
from app.utils.update_at_trigger import updatedAtTrigger

load_dotenv()


class SocialMongoDB(SocialRepository):
    db_url = environ.get("MONGO_URL")
    client = pymongo.MongoClient(db_url)

    def __init__(self):
        self.database = self.client["social_service"]
        self.posts_collection = self.database["posts"]
        self.users_collection = self.database["users"]

    def shutdown(self):
        self.client.close()

    def rollback(self):
        pass

    def clean_table(self, table: Base):
        self.database.drop_collection(table.__collectionname__)

    @withMongoExceptionsHandle()
    def add_post(self, record: Base) -> Optional[str]:
        now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).isoformat()[:-6]
        record_dump = record.model_dump(by_alias=True, exclude=["id"])
        record_dump["created_at"] = now
        record_dump["updated_at"] = now
        result = self.posts_collection.insert_one(record_dump)
        if result.inserted_id:
            return str(result.inserted_id)

    @withMongoExceptionsHandle()
    def get_post(self, id_post: str) -> Post:
        result = self.posts_collection.find_one({"_id": ObjectId(id_post)})
        if result is None:
            raise ItemNotFound("Post", id_post)

        result["id"] = str(result["_id"])
        return result

    @updatedAtTrigger(collection_name="posts")
    @withMongoExceptionsHandle()
    def update_post(self, id_post: str, update_post_set: str) -> Optional[int]:
        """
        Delete a post by id and its logs
        Args:
            id_post (str): id of the post to update
            update_post_set (str): json string with the fields to update
        Returns:
            int: number of rows affected. 0 if no rows were affected
        Decorators:
            - withMongoExceptionsHandle: Decorator to handle exceptions from MongoDB
            - updatedAtTrigger: Decorator to update
            the updated_at!!
        """
        if not update_post_set:
            return

        result = self.posts_collection.update_one(
            {"_id": ObjectId(id_post)}, {"$set": json.loads(update_post_set)}
        )
        return result.modified_count

    @withMongoExceptionsHandle()
    def delete_post(self, id_received: str) -> int:
        """
        Delete a post by id and its logs
        Args:
            id_received (str): id of the post to delete
        Returns:
            int: number of rows affected. 0 if no rows were affected
        """
        result = self.posts_collection.delete_one({"_id": ObjectId(id_received)})
        return result.deleted_count
