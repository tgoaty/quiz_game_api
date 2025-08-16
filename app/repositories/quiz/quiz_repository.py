from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Quiz, Question, AnswerOption
from app.repositories.BaseRepository import BaseRepository
from app.schemas import (
    QuestionCreate,
    AnswerOptionCreate,
    AnswerOptionUpdate,
    QuestionUpdate,
)
from app.schemas.quiz.quiz import QuizCreate, QuizUpdate


class QuizRepository(BaseRepository[Quiz, QuizCreate, QuizUpdate]):
    async def create_with_relations(
        self, db: AsyncSession, quiz_data: QuizCreate
    ) -> Quiz:
        quiz = Quiz(**quiz_data.model_dump(exclude={"questions"}))
        db.add(quiz)
        await db.flush()

        for question_data in quiz_data.questions:
            question = Question(
                **question_data.model_dump(exclude={"answer_options"}),
                quiz_sid=quiz.sid,
            )
            db.add(question)
            await db.flush()

            for option_data in question_data.answer_options:
                option = AnswerOption(
                    **option_data.model_dump(), question_sid=question.sid
                )
                db.add(option)

        await db.commit()
        await db.refresh(quiz)
        return quiz


class QuestionRepository(BaseRepository[Question, QuestionCreate, QuestionUpdate]):
    async def create_with_answers(
        self, db: AsyncSession, question_data: QuestionCreate, quiz_sid: UUID
    ) -> Question:
        question_dict = question_data.model_dump()
        question_dict["quiz_sid"] = quiz_sid

        question = await self.create(db, question_dict)

        answer_repo = AnswerOptionRepository()
        for answer_data in question_data.answer_options:
            await answer_repo.create(
                db, {**answer_data.model_dump(), "question_sid": question.sid}
            )

        return question


class AnswerOptionRepository(
    BaseRepository[AnswerOption, AnswerOptionCreate, AnswerOptionUpdate]
):
    pass


quiz_repository = QuizRepository(Quiz)
question_repository = QuestionRepository(Question)
answer_option_repository = AnswerOptionRepository(AnswerOption)
