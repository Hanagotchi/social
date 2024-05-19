from datetime import datetime
import logging
from fastapi import Depends, FastAPI, Query, Request, Body
from app.controller.Social import SocialController
from app.service.Social import SocialService
from typing import Annotated
from app.repository.SocialMongo import SocialMongoDB
from app.schemas.Post import (
    PostCreateSchema,
    PostFilters,
    PostPagination,
    PostPartialUpdateSchema,
    TagType,
)
from app.security.JWTBearer import get_current_user_id
from app.schemas.SocialUser import (
    SocialUserCreateSchema,
    FollowUserSchema,
    TagSchema
)

app = FastAPI(
    title="Social API",
    version="0.1.0",
    summary="Microservice for social network management",
)

social_repository = SocialMongoDB()
social_service = SocialService(social_repository)
social_controller = SocialController(social_service)

logger = logging.getLogger("social")
logger.setLevel("DEBUG")


@app.on_event("startup")
async def start_up():
    app.logger = logger

    try:
        app.logger.info("Postgres connection established")
    except Exception as e:
        app.logger.error(e)
        app.logger.error("Could not connect to Postgres client")


@app.on_event("shutdown")
async def shutdown_db_client():
    social_repository.shutdown()
    app.logger.info("Postgres shutdown succesfully")


@app.post("/social/posts", tags=["Posts"])
async def create_post(item: PostCreateSchema):
    return await social_controller.handle_create_post(item)


@app.get("/social/posts/{id_post}", tags=["Posts"])
async def get_one_post(req: Request, id_post: str):
    return await social_controller.handle_get_post(id_post)


@app.patch(
    "/social/posts/{id_post}",
    tags=["Posts"],
)
async def update_fields_in_post(
    id_post: str,
    update_post_set: PostPartialUpdateSchema = Body(...),
):
    return await social_controller.handle_update_post(id_post, update_post_set)


@app.delete(
    "/social/posts/{id_post}",
    tags=["Posts"],
)
def delete_post(id_post: str):
    return social_controller.handle_delete_post(id_post)


@app.get(
    "/social/users/me/feed",
    tags=["Social User"],
)
async def get_my_feed(
    user_id: Annotated[int, Depends(get_current_user_id)],
    time_offset: Annotated[datetime | None, Query(default_factory=datetime.today)],
    page: Annotated[int | None, Query(ge=1)] = 1,
    per_page: Annotated[int | None, Query(ge=1, le=100)] = 30,
):
    return await social_controller.handle_get_my_feed(
        user_id, PostPagination(time_offset=time_offset, page=page, per_page=per_page)
    )


@app.get("/social/users/{id_user}", tags=["Social User"])
async def get_social_user(id_user: int):
    return await social_controller.handle_get_social_user(id_user)


@app.post(
    "/social/users",
    tags=["Social User"],
)
async def create_social_user(item: SocialUserCreateSchema):
    return await social_controller.handle_create_social_user(item)


@app.get("/social/posts", tags=["Posts"])
async def get_all_posts(
    time_offset: Annotated[datetime | None, Query(default_factory=datetime.today)],
    page: Annotated[int | None, Query(ge=1)] = 1,
    per_page: Annotated[int | None, Query(ge=1, le=100)] = 30,
    tag: Annotated[TagType | None, Query(default_factory=None)] = None,
    author: Annotated[int | None, Query(ge=1)] = None,
):
    return await social_controller.handle_get_all(
        PostFilters(
            pagination=PostPagination(
                time_offset=time_offset, page=page, per_page=per_page
            ),
            tags=tag.lower() if tag else None,
            users=[author] if author else None,
        ),
    )


@app.post(
    "/social/users/follow",
    tags=["Social User"],
)
async def follow_social_user(
    user_id: Annotated[int, Depends(get_current_user_id)],
    user_to_follow_id: FollowUserSchema = Body(...)
):
    return await social_controller.handle_follow_social_user(user_id,
                                                             user_to_follow_id.user_id)


@app.post(
    "/social/users/unfollow",
    tags=["Social User"],
)
async def unfollow_social_user(
    user_id: Annotated[int, Depends(get_current_user_id)],
    user_to_unfollow_id: FollowUserSchema = Body(...)
):
    return await social_controller.handle_unfollow_social_user(
        user_id,
        user_to_unfollow_id.user_id
    )


@app.post(
    "/social/users/tags/subscribe",
    tags=["Social User"],
)
async def subscribe_to_tag(
    user_id: Annotated[int, Depends(get_current_user_id)],
    tag: TagSchema = Body(...)
):
    return await social_controller.handle_subscribe_to_tag(
        user_id,
        tag
    )


@app.post(
    "/social/users/tags/unsubscribe",
    tags=["Social User"],
)
async def unsubscribe_to_tag(
    user_id: Annotated[int, Depends(get_current_user_id)],
    tag: TagSchema = Body(...)
):
    return await social_controller.handle_unsubscribe_to_tag(
        user_id,
        tag
    )
