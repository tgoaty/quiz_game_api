from fastapi import FastAPI
from app.routers import api_router
from app.core.docs.tags_description import openapi_tags

app = FastAPI(
    title="QuizGameAPI",
    version="0.1.0",
    description="API for the best Quiz Game",
    openapi_tags=openapi_tags,
)

app.include_router(api_router)
