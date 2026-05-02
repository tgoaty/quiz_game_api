from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base_model import Base

QUIZ_SCHEMA = "quizzes"


class SessionAnswer(Base):
    __tablename__ = "session_answer"
    __table_args__ = (
        UniqueConstraint(
            "participant_sid",
            "question_sid",
            name="uq_session_answer_participant_question",
        ),
        {"schema": QUIZ_SCHEMA, "comment": "Participant answers in quiz sessions"},
    )

    participant_sid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("quizzes.session_participant.sid", ondelete="CASCADE"),
        nullable=False,
        comment="Participant ID",
    )
    question_sid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("quizzes.question.sid", ondelete="CASCADE"),
        nullable=False,
        comment="Question ID",
    )
    answer_option_sid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("quizzes.answer_option.sid", ondelete="CASCADE"),
        nullable=False,
        comment="Answer option ID",
    )
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    participant = relationship("SessionParticipant", back_populates="answer")
    question = relationship("Question")
    answer_option = relationship("AnswerOption")
