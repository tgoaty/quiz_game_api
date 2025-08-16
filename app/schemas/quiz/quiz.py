from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas import QuestionCreate
from app.schemas.CoreModel import CoreModel
from app.schemas.quiz.question import QuestionInfo


class QuizBase(CoreModel):
    title: str = Field(..., description="Title of the quiz")
    description: Optional[str] = Field(None, description="Description of the quiz")


class QuizCreate(QuizBase):
    title: str = Field(..., description="Title of the quiz")
    description: Optional[str] = Field(None, description="Description of the quiz")
    question: Optional[list[QuestionCreate]] = Field(
        None, description="List of questions"
    )


class QuizUpdate(QuizBase):
    title: Optional[str] = Field(None, description="Title of the quiz")
    description: Optional[str] = Field(None, description="Description of the quiz")


class QuizInfo(QuizBase):
    sid: UUID = Field(..., description="UUID of the quiz")
    question: Optional[list[QuestionInfo]] = Field(
        None, description="List of questions"
    )
