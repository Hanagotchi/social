import datetime
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
        now = datetime.datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
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

    @withMongoExceptionsHandle()
    def update_publication(self, id_publication: str, content: Optional[str]):
        pass

    @withMongoExceptionsHandle()
    def delete_publication(self, id_received: str) -> int:
        pass
