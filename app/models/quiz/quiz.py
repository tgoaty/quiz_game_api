from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base_model import Base

QUIZ_SCHEMA = "quizzes"


class Quiz(Base):
    __tablename__ = "quiz"
    __table_args__ = {"schema": QUIZ_SCHEMA, "comment": "Table with all quizzes"}

    title: Mapped[str] = mapped_column(String, nullable=False, comment="Quiz title")
    description: Mapped[str] = mapped_column(
        String, nullable=True, comment="quiz description"
    )

    question = relationship(
        "Question", back_populates="quiz", cascade="all, delete-orphan", lazy="joined"
    )
