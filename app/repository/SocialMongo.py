from datetime import datetime
from zoneinfo import ZoneInfo
from bson import ObjectId
import pymongo
from dotenv import load_dotenv
from os import environ
from app.models.base import Base
from app.models.Publication import Publication
from typing import Optional
from app.repository.SocialRepository import SocialRepository
from app.exceptions.NotFoundException import ItemNotFound
from app.utils.mongo_exception_handling import withMongoExceptionsHandle
from app.utils.update_at_trigger import updateAtTrigger

load_dotenv()


class SocialMongoDB(SocialRepository):
    db_url = environ.get("MONGO_URL")
    client = pymongo.MongoClient(db_url)

    def __init__(self):
        self.database = self.client["social_service"]
        self.publications_collection = self.database["publications"]
        self.users_collection = self.database["users"]

    def shutdown(self):
        self.client.close()

    def rollback(self):
        pass

    def clean_table(self, table: Base):
        self.database.drop_collection(table.__collectionname__)

    @withMongoExceptionsHandle()
    def add_publication(self, record: Base) -> Optional[str]:
        now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).isoformat()[:-6]
        record_dump = record.model_dump(by_alias=True, exclude=["id"])
        record_dump["created_at"] = now
        record_dump["updated_at"] = now
        result = self.publications_collection.insert_one(record_dump)
        if result.inserted_id:
            return str(result.inserted_id)

    @withMongoExceptionsHandle()
    def get_publication(self, id_publication: str) -> Publication:
        result = self.publications_collection.find_one(
            {"_id": ObjectId(id_publication)}
        )
        if result is None:
            raise ItemNotFound("Publication", id_publication)

        result["id"] = str(result["_id"])
        return result

    @updateAtTrigger()
    @withMongoExceptionsHandle()
    def update_publication(
        self, id_publication: str, content: Optional[str]
    ) -> Optional[int]:
        """
        Delete a publication by id and its logs
        Args:
            id_publication (str): id of the publication to update
            content (str): new content to update
        Returns:
            int: number of rows affected. 0 if no rows were affected
        Decorators:
            - withMongoExceptionsHandle: Decorator to handle exceptions from MongoDB
            - updateAtTrigger: Decorator to update the updated_at field in the publication!
        """
        if not content:
            return

        result = self.publications_collection.update_one(
            {"_id": ObjectId(id_publication)},
            {"$set": {"content": content}},
        )
        return result.modified_count

    @withMongoExceptionsHandle()
    def delete_publication(self, id_received: str) -> int:
        """
        Delete a publication by id and its logs
        Args:
            id_received (str): id of the publication to delete
        Returns:
            int: number of rows affected. 0 if no rows were affected
        """
        print(f"[REPOSITORY] delete {id_received}")
        result = self.publications_collection.delete_one({"_id": ObjectId(id_received)})
        return result.deleted_count
