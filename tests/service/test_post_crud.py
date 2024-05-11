import pytest
import logging
import mongomock
import os
import re

from dotenv import load_dotenv
from app.repository.SocialMongo import SocialMongoDB
from httpx import Response
from app.schemas.Post import PostCreateSchema, PostPartialUpdateSchema, PostSchema
from app.service.Social import SocialService
from app.schemas.RealUser import ReducedUser
from app.exceptions.\
    InternalServerErrorException import InternalServerErrorException
from fastapi import HTTPException

from app.exceptions.NotFoundException import ItemNotFound


load_dotenv()
logger = logging.getLogger("app")
logger.setLevel("DEBUG")


async def mock_get_user_service_with_id_1(*args, **kwargs):
    response = Response(status_code=200)
    if re.match(r"^/users/\d+$", str(args[0])):
        path_parts = str(args[0]).split("/")
        user_id = int(path_parts[-1])
        if user_id != 1:
            logger.error(f"User {user_id} not found")
            return HTTPException(status_code=404, detail=f"User with id {user_id} not found!")

        response.json = lambda: {"message": {
            "id": user_id,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "gender": "HOMBRE",
            "photo": "https://example.com/photo.jpg",
            "birthdate": "1990-01-01",
            "location": {"lat": 0.0, "lonG": 0.0},
            "nickname": "johndoe",
            "biography": "I am a developer",
        }}

        return response


@pytest.fixture(autouse=True)
def test(monkeypatch):
    # Mocking UserService.get
    monkeypatch.setattr("app.service.Users.UserService.get", mock_get_user_service_with_id_1)
    # Mocking MongoClient!
    db = mongomock.MongoClient()

    def fake_mongo(*args, **kwargs):
        return db

    monkeypatch.setattr('app.repository.SocialMongo.SocialMongoDB.get_client', fake_mongo)

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
        tags=["tag1", "tag2"]
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
    input_post = PostCreateSchema(
        author_user_id=2,
        content="Hello world"
    )

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
        tags=["tag1", "tag2"]
    )
    res_create_post: PostSchema = await social_service.create_post(input_post)
    post_id = res_create_post.id

    # When
    res_get_post: PostSchema = await social_service.get_post(post_id)

    # Then
    assert res_get_post == res_create_post
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
    assert str(excinfo.value) == "404: Post with id 123c252869510e3f2d442b7e not found"

@pytest.mark.asyncio
async def test_given_post_id_when_update_one_field_then_return_post_schema_with_updated_field():
    # Given
    input_post = PostCreateSchema(
        author_user_id=1,
        content="Hello world",
        photo_links=["https://example.com/photo.jpg"],
        tags=["tag1", "tag2"]
    )
    res_create_post: PostSchema = await social_service.create_post(input_post)
    post_id = res_create_post.id
    input_post_to_update = PostPartialUpdateSchema(
        content="Hello world updated"
    )

    # When
    res_update_post: PostSchema = await social_service.update_post(post_id, input_post_to_update)

    # Then
    assert res_update_post.content == "Hello world updated"
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
        photo_links=["https://example.com/photo2_new.jpg"],
    )

    # When
    res_update_post: PostSchema = await social_service.update_post(post_id, input_post_to_update)

    # Then
    assert res_update_post.content == "Hello world updated"
    assert res_update_post.photo_links == ["https://example.com/photo2_new.jpg"]


@pytest.mark.asyncio
async def test_given_post_id_when_update_tags_then_return_post_schema_with_new_tags():
    # Given
    input_post = PostCreateSchema(
        author_user_id=1,
        content="Hello world",
        tags=["tag1", "tag2"]
    )
    res_create_post: PostSchema = await social_service.create_post(input_post)
    post_id = res_create_post.id
    input_post_to_update = PostPartialUpdateSchema(
        content="Hello world updated",
        tags=["tag3", "tag4"],
    )

    # When
    res_update_post: PostSchema = await social_service.update_post(post_id, input_post_to_update)

    # Then
    assert res_update_post.content == "Hello world updated"
    assert res_update_post.photo_links == []
    assert res_update_post.tags == ["tag3", "tag4"]

@pytest.mark.asyncio
async def test_given_post_id_when_update_all_fields_then_return_post_schema_with_updated_fields():
    # Given
    input_post = PostCreateSchema(
        author_user_id=1,
        content="Hello world",
        tags=["tag1", "tag2"]
    )
    res_create_post: PostSchema = await social_service.create_post(input_post)
    post_id = res_create_post.id
    input_post_to_update = PostPartialUpdateSchema(
        content="Hello world updated",
        photo_links=["https://example.com/photo2_new.jpg"],
        tags=["tag3", "tag4"],
    )

    # When
    res_update_post: PostSchema = await social_service.update_post(post_id, input_post_to_update)

    # Then
    assert res_update_post.content == "Hello world updated"
    assert res_update_post.photo_links == ["https://example.com/photo2_new.jpg"]
    assert res_update_post.tags == ["tag3", "tag4"]

@pytest.mark.asyncio
async def test_given_post_id_when_delete_post_then_return_one_as_number_of_rows_affected():
    # Given
    input_post = PostCreateSchema(
        author_user_id=1,
        content="Hello world",
        tags=["tag1", "tag2"]
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
