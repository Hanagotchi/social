import logging
from fastapi import FastAPI, Request, Body
from app.controller.Social import SocialController
from app.service.Social import SocialService

from app.repository.SocialMongo import SocialMongoDB
from app.schemas.Post import (
    PostCreateSchema,
    PostPartialUpdateSchema,
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


@app.post("/posts", tags=["Posts"])
async def create_post(item: PostCreateSchema):
    return await social_controller.handle_create_post(item)


@app.get("/posts/{id_post}", tags=["Posts"])
async def get_one_post(req: Request, id_post: str):
    return social_controller.handle_get_post(id_post)


@app.patch(
    "/posts/{id_post}",
    tags=["Posts"],
)
async def update_fields_in_post(
    id_post: str,
    post_update_set: PostPartialUpdateSchema = Body(...),
):
    return social_controller.handle_update_post(id_post, post_update_set)


@app.delete(
    "/posts/{id_post}",
    tags=["Posts"],
)
def delete_post(id_post: str):
    return social_controller.handle_delete_post(id_post)
