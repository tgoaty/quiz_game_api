from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.CoreModel import CoreModel
from app.schemas.quiz.answer_option import (
    AnswerOptionCreate,
    AnswerOptionInfo,
)


class QuestionBase(CoreModel):
    text: str = Field(..., description="Text of the question")
    order_num: int = Field(..., description="Order number of the question")


class QuestionCreate(QuestionBase):
    text: str = Field(..., description="Text of the question")
    order_num: int = Field(..., description="Order number of the question")
    answer_option: Optional[list[AnswerOptionCreate]] = Field(
        None, description="List of answer options"
    )


class QuestionUpdate(QuestionBase):
    text: Optional[str] = Field(None, description="Text of the question")
    order_num: Optional[int] = Field(None, description="Order number of the question")
    quiz_sid: Optional[UUID] = Field(None, description="UUID of the quiz")


class QuestionInfo(QuestionBase):
    sid: UUID = Field(..., description="UUID of the question")
    answer_option: Optional[list[AnswerOptionInfo]] = Field(
        None, description="List of answer options"
    )

    class Config:
        from_attributes = True
