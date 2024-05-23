from asyncio import sleep
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
import pytest
import logging
import mongomock
import re

from dotenv import load_dotenv
from app.repository.SocialMongo import SocialMongoDB
from httpx import Response
from app.schemas.Post import (
    PostCommentSchema,
    PostCreateSchema,
    PostPagination,
    PostPartialUpdateSchema,
    PostSchema,
)
from app.service.Social import SocialService
from app.schemas.RealUser import ReducedUser
from app.exceptions.InternalServerErrorException \
    import InternalServerErrorException
from fastapi import HTTPException

from app.exceptions.NotFoundException import ItemNotFound
from app.schemas.SocialUser import SocialUserCreateSchema
from app.schemas.SocialUser import UserSchema
from app.exceptions.BadRequestException import BadRequestException


load_dotenv()
logger = logging.getLogger("app")
logger.setLevel("DEBUG")


async def mock_get_user_service_with_three_valid_ids(*args, **kwargs):
    response = Response(status_code=200)

    # [PATH]: /users?ids=1, 5, 10 or /users?ids=1, 5 or /users?ids=1
    if re.match(r"^/users\?ids=(\d+(,\s*\d+)*)", str(args[0])):
        print(f"[PATH 2]: {args[0]}")
        path_parts = str(args[0]).split("=")
        print(f"[PATH PARTS]: {path_parts}")
        users_ids = list(map(int, path_parts[-1].split(",")))
        print(f"[USERS IDS a ]: {users_ids}")
        if 1 not in users_ids and 5 not in users_ids and 10 not in users_ids:
            logger.error(f"Users {users_ids} not found")
            return HTTPException(
                status_code=404, detail=f"Users with ids {users_ids} not found"
            )
        print(f"[USERS IDS b ]: {users_ids}")

        response.json = lambda: {
            "message": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "gender": "HOMBRE",
                    "photo": "https://example.com/photo.jpg",
                    "birthdate": "1990-01-01",
                    "location": {"lat": 0.0, "lonG": 0.0},
                    "nickname": "johndoe",
                    "biography": "I am a developer",
                },
                {
                    "id": 5,
                    "name": "Lisa Simpson",
                    "email": "lisa@example.com",
                    "gender": "MUJER",
                    "photo": "https://example.com/photo_lisa.jpg",
                    "birthdate": "1998-01-01",
                    "location": {"lat": 0.0, "lonG": 0.0},
                    "nickname": "lisa_simspon",
                    "biography": "I am artist",
                },
                {
                    "id": 10,
                    "name": "Bart Simpson",
                    "email": "bart@example.com",
                    "gender": "HOMBRE",
                    "photo": "https://example.com/photo_bart.jpg",
                    "birthdate": "1995-01-01",
                    "location": {"lat": 0.0, "lonG": 0.0},
                    "nickname": "bart_simpson",
                    "biography": "I am artist",
                },
            ]
        }
        return response

    if re.match(r"^/users/\d+$", str(args[0])):
        path_parts = str(args[0]).split("/")
        user_id = int(path_parts[-1])
        if user_id != 1 and user_id != 5 and user_id != 10:
            logger.error(f"User {user_id} not found")
            return HTTPException(
                status_code=404, detail=f"User with id {user_id} not found!"
            )

        response.json = lambda: {
            "message": {
                "id": user_id,
                "name": "John Doe",
                "email": "john.doe@example.com",
                "gender": "HOMBRE",
                "photo": "https://example.com/photo.jpg",
                "birthdate": "1990-01-01",
                "location": {"lat": 0.0, "lonG": 0.0},
                "nickname": "johndoe",
                "biography": "I am a developer",
            }
        }

        return response


@pytest.fixture(autouse=True)
def test(monkeypatch):
    # Mocking UserService.get
    monkeypatch.setattr(
        "app.external.Users.UserService.get",
        mock_get_user_service_with_three_valid_ids
    )
    # Mocking MongoClient!
    db = mongomock.MongoClient()

    def fake_mongo(*args, **kwargs):
        return db

    monkeypatch.setattr(
        "app.repository.SocialMongo.SocialMongoDB.get_client", fake_mongo
    )

    social_repository = SocialMongoDB()
    global social_service
    social_service = SocialService(social_repository)


@pytest.mark.asyncio
async def test_given_post_create_schema_when_create_post_then_return_post_schema():
    # Given
    input_post = PostCreateSchema(
        author_user_id=1,
        content="Hello world",
        photo_links=["https://example.com/photo.jpg"],
        tags=["tag1", "tag2"],
    )

    # When
    res: PostSchema = await social_service.create_post(input_post)

    # Then
    assert res.content == "Hello world"
    assert res.photo_links == ["https://example.com/photo.jpg"]
    assert res.tags == ["tag1", "tag2"]
    assert res.author == ReducedUser(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        photo="https://example.com/photo.jpg",
        nickname="johndoe",
    )


@pytest.mark.asyncio
async def test_given_post_create_with_inexistent_user_when_create_post_then_raise_internal_server_error_exception():
    # Given
    input_post = PostCreateSchema(author_user_id=2, content="Hello world")

    # When
    with pytest.raises(InternalServerErrorException) as excinfo:
        await social_service.create_post(input_post)

    # Then
    assert str(excinfo.value) == "500: An error occurred in the User service"


@pytest.mark.asyncio
async def test_given_post_created_when_get_post_by_id_then_return_post_schema():
    # Given
    input_post = PostCreateSchema(
        author_user_id=1,
        content="Hello world",
        photo_links=["https://example.com/photo.jpg"],
        tags=["tag1", "tag2"],
    )
    res_create_post: PostSchema = await social_service.create_post(input_post)
    post_id = res_create_post.id

    # When
    res_get_post: PostSchema = await social_service.get_post(post_id)

    # Then
    assert res_get_post.id == res_create_post.id
    assert res_get_post.content == "Hello world"
    assert res_get_post.photo_links == ["https://example.com/photo.jpg"]
    assert res_get_post.tags == ["tag1", "tag2"]
    assert res_get_post.author == ReducedUser(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        photo="https://example.com/photo.jpg",
        nickname="johndoe",
    )


@pytest.mark.asyncio
async def test_given_post_id_not_found_when_get_post_by_id_then_raise_not_found_exception():
    # Given
    post_id = "123c252869510e3f2d442b7e"

    # When
    with pytest.raises(ItemNotFound) as excinfo:
        await social_service.get_post(post_id)

    # Then
    assert str(excinfo.value) == "404: Post with id " + \
        "123c252869510e3f2d442b7e not found"


@pytest.mark.asyncio
async def test_given_post_id_when_update_one_field_then_return_post_schema_with_updated_field():
    # Given
    input_post = PostCreateSchema(
        author_user_id=1,
        content="Hello world",
        photo_links=["https://example.com/photo.jpg"],
        tags=["tag1", "tag2"],
    )
    res_create_post: PostSchema = await social_service.create_post(input_post)
    post_id = res_create_post.id
    input_post_to_update = PostPartialUpdateSchema(content="Hello updated")

    # When
    res_update_post: PostSchema = await social_service.update_post(
        post_id, input_post_to_update
    )

    # Then
    assert res_update_post.content == "Hello updated"
    assert res_update_post.photo_links == ["https://example.com/photo.jpg"]
    assert res_update_post.tags == ["tag1", "tag2"]
    assert res_update_post.author == ReducedUser(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        photo="https://example.com/photo.jpg",
        nickname="johndoe",
    )


@pytest.mark.asyncio
async def test_given_post_id_when_update_photo_links_then_return_post_schema_with_new_photo_links():
    # Given
    input_post = PostCreateSchema(
        author_user_id=1,
        content="Hello world",
        photo_links=["https://example.com/photo.jpg"],
    )
    res_create_post: PostSchema = await social_service.create_post(input_post)
    post_id = res_create_post.id
    input_post_to_update = PostPartialUpdateSchema(
        content="Hello world updated",
        photo_links=["https://exampl.com/photo2_new.jpg"],
    )

    # When
    res_update_post: PostSchema = await social_service.update_post(
        post_id, input_post_to_update
    )

    # Then
    assert res_update_post.content == "Hello world updated"
    assert res_update_post.photo_links == ["https://exampl.com/photo2_new.jpg"]


@pytest.mark.asyncio
async def test_given_post_id_when_update_tags_then_return_post_schema_with_new_tags():
    # Given
    input_post = PostCreateSchema(
        author_user_id=1, content="Hello world", tags=["tag1", "tag2"]
    )
    res_create_post: PostSchema = await social_service.create_post(input_post)
    post_id = res_create_post.id
    input_post_to_update = PostPartialUpdateSchema(
        content="Hello world updated",
        tags=["tag3", "tag4"],
    )

    # When
    res_update_post: PostSchema = await social_service.update_post(
        post_id, input_post_to_update
    )

    # Then
    assert res_update_post.content == "Hello world updated"
    assert res_update_post.photo_links == []
    assert res_update_post.tags == ["tag3", "tag4"]


@pytest.mark.asyncio
async def test_given_post_id_when_update_all_fields_then_return_post_schema_with_updated_fields():
    # Given
    input_post = PostCreateSchema(
        author_user_id=1, content="Hello world", tags=["tag1", "tag2"]
    )
    res_create_post: PostSchema = await social_service.create_post(input_post)
    post_id = res_create_post.id
    input_post_to_update = PostPartialUpdateSchema(
        content="Hello world updated",
        photo_links=["https://exampl.com/photo2_new.jpg"],
        tags=["tag3", "tag4"],
    )

    # When
    res_update_post: PostSchema = await social_service.update_post(
        post_id, input_post_to_update
    )

    # Then
    assert res_update_post.content == "Hello world updated"
    assert res_update_post.photo_links == ["https://exampl.com/photo2_new.jpg"]
    assert res_update_post.tags == ["tag3", "tag4"]


@pytest.mark.asyncio
async def test_given_post_id_when_delete_post_then_return_one_as_number_of_rows_affected():
    # Given
    input_post = PostCreateSchema(
        author_user_id=1, content="Hello world", tags=["tag1", "tag2"]
    )
    res_create_post: PostSchema = await social_service.create_post(input_post)
    post_id = res_create_post.id

    # When
    res_delete_post = social_service.delete_post(post_id)

    # Then
    assert res_delete_post == 1


@pytest.mark.asyncio
async def test_given_post_id_inexistent_when_delete_post_then_return_zero_as_number_of_rows_affected():
    # Given
    post_id_inexistent = "123c252869510e3f2d442b7e"

    # When
    res_delete_post = social_service.delete_post(post_id_inexistent)

    # Then
    assert res_delete_post == 0


@pytest.mark.asyncio
async def test_given_user_id_exists_when_create_social_user_then_return_social_user_schema():
    # Given
    input_user = SocialUserCreateSchema(id=1)

    # When
    res_create_user = await social_service.create_social_user(input_user)

    # Then
    assert res_create_user.id == 1
    assert res_create_user.followers == []
    assert res_create_user.following == []
    assert res_create_user.tags == []


@pytest.mark.asyncio
async def test_given_user_id_not_exists_when_create_social_user_then_raise_bad_request_exception():
    # Given
    input_user = SocialUserCreateSchema(id=2)

    # When
    with pytest.raises(BadRequestException) as excinfo:
        await social_service.create_social_user(input_user)

    # Then
    assert str(excinfo.value) == "400: Bad request: " + \
        "user does not exist in the system!"


@pytest.mark.asyncio
async def test_given_social_user_when_get_social_user_then_return_user_schema():
    # Given
    input_user = SocialUserCreateSchema(id=1)
    res_create_user = await social_service.create_social_user(input_user)

    # When
    res_get_user = await social_service.get_social_user(res_create_user.id)

    # Then
    assert res_get_user.id == 1
    assert res_get_user.followers == []
    assert res_get_user.following == []
    assert res_get_user.tags == []
    assert res_get_user.name == "John Doe"
    assert res_get_user.photo == "https://example.com/photo.jpg"
    assert res_get_user.nickname == "johndoe"


@pytest.mark.asyncio
async def test_given_social_user_inexistent_when_get_social_user_then_raise_item_not_found_exception():
    # Given
    user_id_inexistent = 2

    # When
    with pytest.raises(ItemNotFound) as excinfo:
        await social_service.get_social_user(user_id_inexistent)

    # Then
    assert str(excinfo.value) == "404: User with id 2 not found"


@pytest.mark.asyncio
async def test_given_social_user_when_follow_social_user_then_follow_user():
    # Given
    input_user_1 = SocialUserCreateSchema(id=1)
    res_create_user_1 = await social_service.create_social_user(input_user_1)
    input_user_2 = SocialUserCreateSchema(id=5)
    res_create_user_2 = await social_service.create_social_user(input_user_2)

    # When
    await social_service.follow_social_user(res_create_user_1.id,
                                            res_create_user_2.id)

    # Then
    res_get_user_1 = await social_service.get_social_user(res_create_user_1.id)
    res_get_user_2 = await social_service.get_social_user(res_create_user_2.id)
    assert res_get_user_1.following == [5]
    assert res_get_user_1.followers == []
    assert res_get_user_2.followers == [1]
    assert res_get_user_2.following == []


@pytest.mark.asyncio
async def test_given_two_social_users_when_follow_mutual_then_follow_each_other():
    # Given
    input_user_1 = SocialUserCreateSchema(id=1)
    res_create_user_1 = await social_service.create_social_user(input_user_1)
    input_user_2 = SocialUserCreateSchema(id=5)
    res_create_user_2 = await social_service.create_social_user(input_user_2)

    # When
    await social_service.follow_social_user(res_create_user_1.id,
                                            res_create_user_2.id)
    await social_service.follow_social_user(res_create_user_2.id,
                                            res_create_user_1.id)

    # Then
    res_get_user_1 = await social_service.get_social_user(res_create_user_1.id)
    res_get_user_2 = await social_service.get_social_user(res_create_user_2.id)
    assert res_get_user_1.following == [5]
    assert res_get_user_1.followers == [5]
    assert res_get_user_2.followers == [1]
    assert res_get_user_2.following == [1]


@pytest.mark.asyncio
async def test_given_social_user_when_follow_itself_then_raise_bad_request_exception():
    # Given
    input_user = SocialUserCreateSchema(id=1)
    res_create_user = await social_service.create_social_user(input_user)

    # When
    with pytest.raises(BadRequestException) as excinfo:
        await social_service.follow_social_user(res_create_user.id,
                                                res_create_user.id)

    # Then
    assert str(excinfo.value) == "400: Bad request: must follow another user"


@pytest.mark.asyncio
async def test_given_social_user_when_follow_inexistent_user_then_raise_bad_request_exception():
    # Given
    input_user = SocialUserCreateSchema(id=1)
    res_create_user = await social_service.create_social_user(input_user)

    # When
    with pytest.raises(BadRequestException) as excinfo:
        await social_service.follow_social_user(res_create_user.id, 2)

    # Then
    assert str(excinfo.value) == "400: Bad request: " + \
        "user does not exist in the system!"


@pytest.mark.asyncio
async def test_given_social_followed_user_when_unfollow_then_unfollow_user():
    # Given
    input_user_1 = SocialUserCreateSchema(id=1)
    res_create_user_1 = await social_service.create_social_user(input_user_1)
    input_user_2 = SocialUserCreateSchema(id=5)
    res_create_user_2 = await social_service.create_social_user(input_user_2)
    await social_service.follow_social_user(res_create_user_1.id,
                                            res_create_user_2.id)

    # When
    await social_service.unfollow_social_user(
        res_create_user_1.id, res_create_user_2.id
    )

    # Then
    res_get_user_1 = await social_service.get_social_user(res_create_user_1.id)
    res_get_user_2 = await social_service.get_social_user(res_create_user_2.id)
    assert res_get_user_1.following == []
    assert res_get_user_1.followers == []
    assert res_get_user_2.followers == []
    assert res_get_user_2.following == []


@pytest.mark.asyncio
async def test_given_social_user_mutual_followed_when_unfollow_then_unfollow_each_other():
    # Given
    input_user_1 = SocialUserCreateSchema(id=1)
    res_create_user_1 = await social_service.create_social_user(input_user_1)
    input_user_2 = SocialUserCreateSchema(id=5)
    res_create_user_2 = await social_service.create_social_user(input_user_2)
    await social_service.follow_social_user(res_create_user_1.id,
                                            res_create_user_2.id)
    await social_service.follow_social_user(res_create_user_2.id,
                                            res_create_user_1.id)

    # When
    await social_service.unfollow_social_user(
        res_create_user_1.id, res_create_user_2.id
    )
    await social_service.unfollow_social_user(
        res_create_user_2.id, res_create_user_1.id
    )

    # Then
    res_get_user_1 = await social_service.get_social_user(res_create_user_1.id)
    res_get_user_2 = await social_service.get_social_user(res_create_user_2.id)
    assert res_get_user_1.following == []
    assert res_get_user_1.followers == []
    assert res_get_user_2.followers == []
    assert res_get_user_2.following == []


@pytest.mark.asyncio
async def test_given_social_user_when_unfollow_itself_then_raise_bad_request_exception():
    # Given
    input_user = SocialUserCreateSchema(id=1)
    res_create_user = await social_service.create_social_user(input_user)

    # When
    with pytest.raises(BadRequestException) as excinfo:
        await social_service.unfollow_social_user(
            res_create_user.id, res_create_user.id
        )

    # Then
    assert str(excinfo.value) == "400: Bad request: must unfollow another user"


@pytest.mark.asyncio
async def test_given_social_user_when_unfollow_inexistent_user_then_raise_bad_request_exception():
    # Given
    input_user = SocialUserCreateSchema(id=1)
    res_create_user = await social_service.create_social_user(input_user)

    # When
    with pytest.raises(BadRequestException) as excinfo:
        await social_service.unfollow_social_user(res_create_user.id, 2)

    # Then
    assert str(excinfo.value) == "400: Bad request:" + \
        " user does not exist in the system!"


@pytest.mark.asyncio
async def test_given_user_with_posts_when_get_my_feed_then_return_posts_showing_most_recent_first():
    # Given
    input_user_1 = SocialUserCreateSchema(id=1)
    res_create_user_1 = await social_service.create_social_user(input_user_1)
    input_post_1_of_user_1 = PostCreateSchema(
        author_user_id=input_user_1.id, content="Hello world 1"
    )
    await social_service.create_post(input_post_1_of_user_1)
    input_post_2_of_user_1 = PostCreateSchema(
        author_user_id=input_user_1.id, content="Hello world 2"
    )

    # ._.
    await sleep(0.1)
    await social_service.create_post(input_post_2_of_user_1)

    # When
    res_get_my_feed = await social_service.get_my_feed(
        res_create_user_1.id,
        PostPagination(time_offset=datetime.now(), page=1, per_page=20),
    )

    # Then
    assert len(res_get_my_feed) == 2
    assert res_get_my_feed[0].content == "Hello world 2"
    assert res_get_my_feed[1].content == "Hello world 1"


@pytest.mark.asyncio
async def test_given_user_without_posts_when_get_my_feed_then_return_empty_list():
    # Given
    input_user_1 = SocialUserCreateSchema(id=1)
    res_create_user_1 = await social_service.create_social_user(input_user_1)

    # When
    res_get_my_feed = await social_service.get_my_feed(
        res_create_user_1.id,
        PostPagination(time_offset=datetime.now(), page=1, per_page=20),
    )

    # Then
    assert res_get_my_feed == []


@pytest.mark.asyncio
async def test_given_user_with_posts_when_get_my_feed_with_one_post_per_page_then_return_posts_paginated():
    # Given
    input_user_1 = SocialUserCreateSchema(id=1)
    res_create_user_1 = await social_service.create_social_user(input_user_1)
    input_post_1_of_user_1 = PostCreateSchema(
        author_user_id=input_user_1.id, content="Hello world 1"
    )
    await social_service.create_post(input_post_1_of_user_1)
    input_post_2_of_user_1 = PostCreateSchema(
        author_user_id=input_user_1.id, content="Hello world 2"
    )

    # ._.
    await sleep(0.1)
    await social_service.create_post(input_post_2_of_user_1)

    # When
    res_get_my_feed = await social_service.get_my_feed(
        res_create_user_1.id,
        PostPagination(time_offset=datetime.now(), page=1, per_page=1),
    )

    # Then
    assert len(res_get_my_feed) == 1
    assert res_get_my_feed[0].content == "Hello world 2"


@pytest.mark.asyncio
async def test_given_user_with_posts_when_get_my_feed_with_other_page_then_return_empty_list():
    # Given
    input_user_1 = SocialUserCreateSchema(id=1)
    res_create_user_1 = await social_service.create_social_user(input_user_1)
    input_post_1_of_user_1 = PostCreateSchema(
        author_user_id=input_user_1.id, content="Hello world 1"
    )
    await social_service.create_post(input_post_1_of_user_1)
    input_post_2_of_user_1 = PostCreateSchema(
        author_user_id=input_user_1.id, content="Hello world 2"
    )

    # ._.
    await sleep(0.1)
    await social_service.create_post(input_post_2_of_user_1)

    # When
    res_get_my_feed = await social_service.get_my_feed(
        res_create_user_1.id,
        PostPagination(time_offset=datetime.now(), page=2, per_page=5),
    )

    # Then
    assert len(res_get_my_feed) == 0


@pytest.mark.asyncio
async def test_given_user_with_posts_when_get_my_feed_with_time_offset_one_day_ago_then_return_empty_list():
    # Given
    input_user_1 = SocialUserCreateSchema(id=1)
    res_create_user_1 = await social_service.create_social_user(input_user_1)
    input_post_1_of_user_1 = PostCreateSchema(
        author_user_id=input_user_1.id, content="Hello world 1"
    )
    await social_service.create_post(input_post_1_of_user_1)
    input_post_2_of_user_1 = PostCreateSchema(
        author_user_id=input_user_1.id, content="Hello world 2"
    )

    # ._.
    await sleep(0.1)
    await social_service.create_post(input_post_2_of_user_1)

    # When
    res_get_my_feed = await social_service.get_my_feed(
        res_create_user_1.id,
        PostPagination(
            time_offset=datetime.now() - timedelta(days=1), page=1, per_page=5
        ),
    )

    # Then
    assert len(res_get_my_feed) == 0


@pytest.mark.asyncio
async def test_given_user_with_posts_and_users_followed_when_get_my_feed_then_return_posts_from_users_followed_and_user_itself():
    # Given
    res_create_user_1 = await social_service.create_social_user(
        SocialUserCreateSchema(id=1)
    )
    res_create_user_2 = await social_service.create_social_user(
        SocialUserCreateSchema(id=5)
    )
    res_create_user_3 = await social_service.create_social_user(
        SocialUserCreateSchema(id=10)
    )

    await social_service.follow_social_user(res_create_user_1.id,
                                            res_create_user_2.id)
    await social_service.follow_social_user(res_create_user_1.id,
                                            res_create_user_3.id)

    await social_service.create_post(
        PostCreateSchema(author_user_id=res_create_user_1.id,
                         content="Hello world 1")
    )
    await sleep(0.1)
    await social_service.create_post(
        PostCreateSchema(author_user_id=res_create_user_2.id,
                         content="Hello world 2")
    )
    await sleep(0.1)
    await social_service.create_post(
        PostCreateSchema(author_user_id=res_create_user_3.id,
                         content="Hello world 3")
    )

    # When
    res_get_my_feed = await social_service.get_my_feed(
        res_create_user_1.id,
        PostPagination(time_offset=datetime.now(), page=1, per_page=5),
    )

    # Then
    assert len(res_get_my_feed) == 3
    assert res_get_my_feed[0].content == "Hello world 3"
    assert res_get_my_feed[1].content == "Hello world 2"
    assert res_get_my_feed[2].content == "Hello world 1"


@pytest.mark.asyncio
async def test_given_user_with_posts_and_users_followed_when_get_my_feed_with_pagination_then_return_posts_paginated():
    # Given
    res_create_user_1 = await social_service.create_social_user(
        SocialUserCreateSchema(id=1)
    )
    res_create_user_2 = await social_service.create_social_user(
        SocialUserCreateSchema(id=5)
    )
    res_create_user_3 = await social_service.create_social_user(
        SocialUserCreateSchema(id=10)
    )

    await social_service.follow_social_user(res_create_user_1.id,
                                            res_create_user_2.id)
    await social_service.follow_social_user(res_create_user_1.id,
                                            res_create_user_3.id)

    await social_service.create_post(
        PostCreateSchema(author_user_id=res_create_user_1.id,
                         content="Hello world 1")
    )
    await sleep(0.1)
    await social_service.create_post(
        PostCreateSchema(author_user_id=res_create_user_2.id,
                         content="Hello world 2")
    )
    await sleep(0.1)
    await social_service.create_post(
        PostCreateSchema(author_user_id=res_create_user_3.id,
                         content="Hello world 3")
    )

    # When (1)
    res_get_my_feed = await social_service.get_my_feed(
        res_create_user_1.id,
        PostPagination(time_offset=datetime.now(), page=1, per_page=2),
    )

    # Then (1)
    assert len(res_get_my_feed) == 2
    assert res_get_my_feed[0].content == "Hello world 3"
    assert res_get_my_feed[1].content == "Hello world 2"

    # When (2)
    res_get_my_feed = await social_service.get_my_feed(
        res_create_user_1.id,
        PostPagination(time_offset=datetime.now(), page=2, per_page=2),
    )

    # Then (2)
    assert len(res_get_my_feed) == 1
    assert res_get_my_feed[0].content == "Hello world 1"

    # When (3)
    res_get_my_feed = await social_service.get_my_feed(
        res_create_user_1.id,
        PostPagination(time_offset=datetime.now(), page=3, per_page=2),
    )

    # Then (3)
    assert len(res_get_my_feed) == 0


@pytest.mark.asyncio
async def test_given_user_with_posts_and_users_followed_when_get_my_feed_with_time_offset_then_return_posts_after_time_offset():
    # Given
    res_create_user_1 = await social_service.create_social_user(
        SocialUserCreateSchema(id=1)
    )
    res_create_user_2 = await social_service.create_social_user(
        SocialUserCreateSchema(id=5)
    )
    res_create_user_3 = await social_service.create_social_user(
        SocialUserCreateSchema(id=10)
    )

    await social_service.follow_social_user(res_create_user_1.id,
                                            res_create_user_2.id)
    await social_service.follow_social_user(res_create_user_1.id,
                                            res_create_user_3.id)

    await social_service.create_post(
        PostCreateSchema(author_user_id=res_create_user_1.id,
                         content="Hello world 1")
    )
    await sleep(0.1)
    post_schema_2 = await social_service.create_post(
        PostCreateSchema(author_user_id=res_create_user_2.id,
                         content="Hello world 2")
    )
    await sleep(0.1)
    await social_service.create_post(
        PostCreateSchema(author_user_id=res_create_user_3.id,
                         content="Hello world 3")
    )

    # When
    res_get_my_feed = await social_service.get_my_feed(
        res_create_user_1.id,
        PostPagination(time_offset=post_schema_2.created_at,
                       page=1,
                       per_page=5),
    )

    # Then
    assert len(res_get_my_feed) == 2
    assert res_get_my_feed[0].content == "Hello world 2"
    assert res_get_my_feed[1].content == "Hello world 1"


@pytest.mark.asyncio
async def test_given_post_when_commented_then_increase_comment_count():
    input_post = PostCreateSchema(
        author_user_id=1,
        content="Hello world",
        photo_links=["https://example.com/photo.jpg"],
        tags=["tag1", "tag2"],
    )
    res_create_post: PostSchema = await social_service.create_post(input_post)
    post_id = res_create_post.id

    # When
    await social_service.comment_post(post_id, 1, "body")

    # Then
    res_get_post: PostSchema = await social_service.get_post(post_id)
    assert res_get_post.comments_count == 1


@pytest.mark.asyncio
async def test_given_post_when_deleted_comment_then_decrease_comment_count():
    input_post = PostCreateSchema(
        author_user_id=1,
        content="Hello world",
        photo_links=["https://example.com/photo.jpg"],
        tags=["tag1", "tag2"],
    )
    res_create_post: PostSchema = await social_service.create_post(input_post)
    post_id = res_create_post.id
    res_comment: PostCommentSchema = await social_service.comment_post(post_id, 1,
                                                                       "body")

    # When
    await social_service.delete_post_comment(post_id, res_comment.id)

    # Then
    res_get_post: PostSchema = await social_service.get_post(post_id)
    assert res_get_post.comments_count == 0


@pytest.mark.asyncio
async def test_get_user_followers_with_no_query(monkeypatch):
    # Given
    user_id = 1
    followers_ids = [2, 3]
    follower_1 = UserSchema(_id=2, name="John Doe", photo="photo1.jpg", nickname="john")
    follower_2 = UserSchema(_id=3, name="Jane Smith", photo="photo2.jpg",
                            nickname="jane")

    monkeypatch.setattr(social_service.social_repository, "get_followers_of",
                        AsyncMock(return_value=followers_ids))

    with patch("app.external.Users.UserService.get_users", return_value=[follower_1,
                                                                        follower_2]):
        # When
        result = await social_service.get_user_followers({"user_id": user_id})

        # Then
        assert len(result) == 2
        assert result[0].id == 2
        assert result[0].name == "John Doe"
        assert result[1].id == 3
        assert result[1].name == "Jane Smith"


@pytest.mark.asyncio
async def test_get_user_followers_returning_empty(monkeypatch):
    # Given
    user_id = 1

    monkeypatch.setattr(social_service.social_repository, "get_followers_of",
                        AsyncMock(return_value=[]))

    with patch("app.external.Users.UserService.get_users", return_value=[]):
        # When
        result = await social_service.get_user_followers({"user_id": user_id,
                                                          "query": "ja"})

        # Then
        assert len(result) == 0


@pytest.mark.asyncio
async def test_get_user_followers_with_query(monkeypatch):
    # Given
    user_id = 1
    followers_ids = [2, 3]
    follower_1 = UserSchema(_id=2, name="John Doe", photo="photo1.jpg",
                            nickname="john")
    follower_2 = UserSchema(_id=3, name="Jane Smith", photo="photo2.jpg",
                            nickname="jane")

    monkeypatch.setattr(social_service.social_repository, "get_followers_of",
                        AsyncMock(return_value=followers_ids))

    with patch("app.external.Users.UserService.get_users", return_value=[follower_1,
                                                                        follower_2]):
        # When
        result = await social_service.get_user_followers({"user_id": user_id,
                                                          "query": "ja"})

        # Then
        assert len(result) == 1
        assert result[0].id == 3
        assert result[0].name == "Jane Smith"


@pytest.mark.asyncio
async def test_get_user_followers_no_user_id():
    # Given
    query_params = {}

    # When / Then
    with pytest.raises(BadRequestException) as excinfo:
        await social_service.get_user_followers(query_params)

    assert str(excinfo.value) == "400: Bad request: user id is required"
