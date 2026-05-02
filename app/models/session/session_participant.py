from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base_model import Base

QUIZ_SCHEMA = "quizzes"


class SessionParticipant(Base):
    __tablename__ = "session_participant"
    __table_args__ = {"schema": QUIZ_SCHEMA, "comment": "Quiz session participants"}

    session_sid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("quizzes.quiz_session.sid", ondelete="CASCADE"),
        nullable=False,
        comment="Session ID",
    )
    name: Mapped[str] = mapped_column(
        String, nullable=False, comment="Participant display name"
    )
    score: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="Correct answers count"
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    session = relationship("QuizSession", back_populates="participant")
    answer = relationship(
        "SessionAnswer",
        back_populates="participant",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
