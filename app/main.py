from fastapi import FastAPI
from app.routers import router

app = FastAPI(
    title="QuizGameAPI",
    version="0.1.0",
    description="API for the best Quiz Game",
)

app.include_router(router)
