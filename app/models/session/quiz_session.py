from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base_model import Base

QUIZ_SCHEMA = "quizzes"


class QuizSession(Base):
    __tablename__ = "quiz_session"
    __table_args__ = {"schema": QUIZ_SCHEMA, "comment": "Live quiz sessions"}

    quiz_sid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("quizzes.quiz.sid", ondelete="CASCADE"),
        nullable=False,
        comment="Quiz ID",
    )
    teacher_name: Mapped[str] = mapped_column(
        String, nullable=False, comment="Teacher display name"
    )
    join_code: Mapped[str] = mapped_column(
        String(12), unique=True, nullable=False, index=True, comment="Student join code"
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="waiting", comment="Session status"
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    quiz = relationship("Quiz")
    participant = relationship(
        "SessionParticipant",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
