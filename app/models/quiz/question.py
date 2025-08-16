from uuid import UUID

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base_model import Base

QUIZ_SCHEMA = "quizzes"


class Question(Base):
    __tablename__ = "question"
    __table_args__ = {"schema": QUIZ_SCHEMA, "comment": "Table with all questions"}

    text: Mapped[str] = mapped_column(String, nullable=False, comment="Question text")
    order_num: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Question order position"
    )

    quiz_sid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("quizzes.quiz.sid", ondelete="CASCADE"),
        nullable=False,
        comment="Quiz ID",
    )
    quiz = relationship("Quiz", back_populates="question")
    answer_option = relationship(
        "AnswerOption",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="joined",
    )
