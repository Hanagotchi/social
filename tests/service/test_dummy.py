import pytest
import logging
import mongomock

from dotenv import load_dotenv
from app.repository.SocialMongo import SocialMongoDB
from httpx import Response
from app.schemas.Post import PostCreateSchema, PostSchema
from app.service.Social import SocialService
from app.schemas.RealUser import ReducedUser

load_dotenv()
logger = logging.getLogger("app")
logger.setLevel("DEBUG")


async def mock_get_user(*args, **kwargs):
    response = Response(status_code=200)
    response.json = lambda: {"message": {
        "id": 1,
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
    monkeypatch.setattr("app.service.Users.UserService.get", mock_get_user)
    
    # Mocking MongoC
    db = mongomock.MongoClient()
    def fake_mongo(*args, **kwargs):
        return db

    monkeypatch.setattr('app.repository.SocialMongo.SocialMongoDB.get_client', fake_mongo)

    social_repository = SocialMongoDB()
    global social_service
    social_service = SocialService(social_repository)


def test_hello_world(test):
    assert 1 == 1


@pytest.mark.asyncio
async def test_given_post_create_schema_when_create_post_then_return_post_schema():
    # Given
    input_post = PostCreateSchema(
        author_user_id=1,
        content="Hello world"
    )

    # When
    res: PostSchema = await social_service.create_post(input_post)

    # Then
    assert res.content == "Hello world"
    assert res.author == ReducedUser(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        photo="https://example.com/photo.jpg",
        nickname="johndoe",
    )


@pytest.mark.asyncio
async def test_given_post_created_when_get_post_by_id_then_return_post_schema():
    # Given
    input_post = PostCreateSchema(
        author_user_id=1,
        content="Hello world"
    )
    res_create_post: PostSchema = await social_service.create_post(input_post)
    post_id = res_create_post.id

    # When
    res_get_post: PostSchema = await social_service.get_post(post_id)

    # Then
    assert res_get_post == res_create_post
