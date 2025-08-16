from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.CoreModel import CoreModel


class AnswerOptionBase(CoreModel):
    text: str = Field(..., description="Text of the answer option")
    is_correct: bool = Field(..., description="Is correct or no")


class AnswerOptionCreate(AnswerOptionBase):
    text: str = Field(..., description="Text of the answer option")
    is_correct: bool = Field(..., description="Is correct or no")


class AnswerOptionUpdate(AnswerOptionBase):
    text: Optional[str] = Field(None, description="Text of the answer option")
    is_correct: Optional[bool] = Field(None, description="Is correct or no")
    question_sid: Optional[UUID] = Field(None, description="UUID of the question")


class AnswerOptionInfo(AnswerOptionBase):
    sid: UUID = Field(..., description="UUID of the answer option")

    class Config:
        from_attributes = True
