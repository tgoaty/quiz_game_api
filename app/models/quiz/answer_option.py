from uuid import UUID

from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base_model import Base

QUIZ_SCHEMA = "quizzes"


class AnswerOption(Base):
    __tablename__ = "answer_option"
    __table_args__ = {"schema": QUIZ_SCHEMA, "comment": "Table with all answer options"}

    text: Mapped[str] = mapped_column(
        String, nullable=False, comment="Answer option text"
    )
    is_correct: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="Right answer or no"
    )

    question_sid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("quizzes.question.sid", ondelete="CASCADE"),
        nullable=False,
        comment="Question ID",
    )
    question = relationship("Question", back_populates="answer_option")
