import logging
from fastapi import FastAPI, Request
from app.controller.Social import SocialController
from app.service.Social import SocialService

from app.repository.SocialMongo import SocialMongoDB
from app.schemas.Publication import (
    PublicationCreateSchema,
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


@app.post("/publications", tags=["Publications"])
async def post_publication(item: PublicationCreateSchema):
    return await social_controller.handle_post_publication(item)


@app.get("/publications/{id_publication}", tags=["Publications"])
async def get_one_publication(req: Request, id_publication: str):
    return social_controller.handle_get_publication(id_publication)
