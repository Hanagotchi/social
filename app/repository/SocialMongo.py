from datetime import datetime
import json
from bson import ObjectId
import pymongo
from dotenv import load_dotenv
from os import environ
from app.models.base import Base
from app.models.Post import Post
from typing import List, Optional
from app.repository.SocialRepository import SocialRepository
from app.exceptions.NotFoundException import ItemNotFound
from app.utils.mongo_exception_handling import withMongoExceptionsHandle
from app.utils.update_at_trigger import updatedAtTrigger
from app.schemas.Post import PostFilters

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
        now = datetime.now()
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

        result["id"] = str(result.pop("_id"))
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
    def update_user(self, id_user: str, update_user_set: str) -> Optional[int]:
       if not update_user_set:
           return

       result = self.users_collection.update_one(
           {"_id": ObjectId(id_user)}, {"$set": json.loads(update_user_set)}
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

    @withMongoExceptionsHandle()
    def get_posts_by(self, filters: PostFilters) -> List[Post]:
        pipeline = [
            {"$match": {"updated_at": {"$lte": filters.pagination.time_offset}}}
        ]
        if filters.tags:
            pipeline.append({"$match": {"tags": filters.tags}})
        if filters.users:
            pipeline.append({"$match": {"author_user_id": {"$in": filters.users}}})

        pipeline += [
            {"$sort": {"updated_at": -1}},  # sort by updated_at desc
            {"$skip": (filters.pagination.page - 1) * filters.pagination.per_page},
            {"$limit": filters.pagination.per_page},
        ]
        cursor = self.posts_collection.aggregate(pipeline)
        posts = []
        for post in cursor:
            post["id"] = str(post.pop("_id"))
            posts.append(post)
        return posts

    @withMongoExceptionsHandle()
    def get_following_of(self, user_id: int) -> List[int]:
        following = list(
            self.users_collection.find({"_id": user_id}, {"following": 1, "_id": 0})
        )
        if not following:
            raise ItemNotFound("Social User", user_id)
        following = following[0].get("following", [])
        return following

    @withMongoExceptionsHandle()
    def get_followers_of(self, user_id: int) -> List[int]:
        followers = list(
            self.users_collection.find({"_id": user_id}, {"followers": 1, "_id": 0})
        )
        if not followers:
            raise ItemNotFound("Social User", user_id)
        followers = followers[0].get("following", [])
        return followers

    @withMongoExceptionsHandle()
    def add_social_user(self, record: Base) -> Optional[int]:
        record_dump = record.model_dump(by_alias=True)
        print(f"[RECORD DUMP]: {record_dump}")
        if "_id" not in record_dump:
            raise Exception("Int id of user is required to add a social user")
        id = record_dump["_id"]
        try:
            self.users_collection.insert_one(record_dump)
            return id
        except pymongo.errors.DuplicateKeyError:
            return id
        except Exception as e:
            raise e

    @withMongoExceptionsHandle()
    def get_social_user(self, id_received: int) -> Base:
        result = self.users_collection.find_one({"_id": id_received})
        if result is None:
            raise ItemNotFound("User", id_received)
        return result
