from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.CoreModel import CoreModel


class SessionAnswerInfo(CoreModel):
    sid: UUID = Field(..., description="UUID of the saved answer")
    question_sid: UUID = Field(..., description="UUID of the question")
    answer_option_sid: UUID = Field(..., description="UUID of the selected answer")
    is_correct: bool = Field(..., description="Whether the answer was correct")


class SessionParticipantInfo(CoreModel):
    sid: UUID = Field(..., description="UUID of the participant")
    name: str = Field(..., description="Participant display name")
    score: int = Field(..., description="Correct answers count")
    completed_at: datetime | None = Field(None, description="Completion timestamp")
    answer: list[SessionAnswerInfo] = Field(
        default_factory=list, description="Participant answers"
    )


class QuizSessionInfo(CoreModel):
    sid: UUID = Field(..., description="UUID of the quiz session")
    quiz_sid: UUID = Field(..., description="UUID of the quiz")
    teacher_name: str = Field(..., description="Teacher display name")
    join_code: str = Field(..., description="Student join code")
    status: str = Field(..., description="Session status")
    started_at: datetime | None = Field(None, description="Start timestamp")
    ended_at: datetime | None = Field(None, description="End timestamp")
    participant: list[SessionParticipantInfo] = Field(
        default_factory=list, description="Session participants"
    )


class SessionResult(CoreModel):
    session: QuizSessionInfo
    total_questions: int
