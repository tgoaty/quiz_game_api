from fastapi import APIRouter

from .quiz import quiz, question, answer_option

api_router = APIRouter(prefix="/api")

api_router.include_router(quiz.router, tags=["Quiz"], prefix="/quiz")
api_router.include_router(question.router, tags=["Question"], prefix="/question")
api_router.include_router(
    answer_option.router, tags=["Answer Option"], prefix="/answer_option"
)
