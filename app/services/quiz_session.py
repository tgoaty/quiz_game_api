from __future__ import annotations

import random
import string
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    AnswerOption,
    Question,
    Quiz,
    QuizSession,
    SessionAnswer,
    SessionParticipant,
)


class QuizSessionError(ValueError):
    pass


class QuizSessionService:
    async def create_session(
        self, db: AsyncSession, *, quiz_sid: UUID, teacher_name: str
    ) -> QuizSession:
        quiz = await self._get_quiz(db, quiz_sid)
        if not quiz:
            raise QuizSessionError("Quiz not found")

        session = QuizSession(
            quiz_sid=quiz.sid,
            teacher_name=teacher_name.strip(),
            join_code=await self._create_join_code(db),
            status="waiting",
        )
        db.add(session)
        await db.commit()
        return await self.get_session(db, session.sid)

    async def join_session(
        self, db: AsyncSession, *, join_code: str, student_name: str
    ) -> SessionParticipant:
        session = await self.get_session_by_code(db, join_code)
        if not session:
            raise QuizSessionError("Session not found")
        if session.status == "finished":
            raise QuizSessionError("Session already finished")

        participant = SessionParticipant(
            session_sid=session.sid,
            name=student_name.strip(),
            score=0,
        )
        db.add(participant)
        await db.commit()
        return participant

    async def start_session(self, db: AsyncSession, session_sid: UUID) -> QuizSession:
        session = await self.get_session(db, session_sid)
        if not session:
            raise QuizSessionError("Session not found")
        if session.status == "finished":
            raise QuizSessionError("Session already finished")

        session.status = "started"
        session.started_at = session.started_at or datetime.utcnow()
        await db.commit()
        return await self.get_session(db, session.sid)

    async def finish_session(self, db: AsyncSession, session_sid: UUID) -> QuizSession:
        session = await self.get_session(db, session_sid)
        if not session:
            raise QuizSessionError("Session not found")

        session.status = "finished"
        session.ended_at = session.ended_at or datetime.utcnow()
        await db.commit()
        return await self.get_session(db, session.sid)

    async def submit_answer(
        self,
        db: AsyncSession,
        *,
        participant_sid: UUID,
        question_sid: UUID,
        answer_option_sid: UUID,
    ) -> SessionAnswer:
        participant = await self._get_participant(db, participant_sid)
        if not participant:
            raise QuizSessionError("Participant not found")

        session = await self.get_session(db, participant.session_sid)
        if not session:
            raise QuizSessionError("Session not found")
        if session.status == "finished":
            raise QuizSessionError("Session already finished")

        question = await self._get_session_question(db, session.quiz_sid, question_sid)
        if not question:
            raise QuizSessionError("Question does not belong to this quiz")

        option = await self._get_question_option(db, question_sid, answer_option_sid)
        if not option:
            raise QuizSessionError("Answer option does not belong to this question")

        saved = await self._get_existing_answer(db, participant_sid, question_sid)
        if saved:
            if saved.is_correct:
                participant.score = max(0, participant.score - 1)
            saved.answer_option_sid = option.sid
            saved.is_correct = option.is_correct
            answer = saved
        else:
            answer = SessionAnswer(
                participant_sid=participant.sid,
                question_sid=question.sid,
                answer_option_sid=option.sid,
                is_correct=option.is_correct,
            )
            db.add(answer)

        if option.is_correct:
            participant.score += 1

        total_questions = await self.count_questions(db, session.quiz_sid)
        answered_count = await self.count_participant_answers(db, participant.sid)
        if answered_count + (0 if saved else 1) >= total_questions:
            participant.completed_at = participant.completed_at or datetime.utcnow()

        await db.commit()
        return answer

    async def get_session(
        self, db: AsyncSession, session_sid: UUID
    ) -> QuizSession | None:
        stmt = (
            select(QuizSession)
            .where(QuizSession.sid == session_sid)
            .options(
                selectinload(QuizSession.participant).selectinload(
                    SessionParticipant.answer
                )
            )
        )
        result = await db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_session_by_code(
        self, db: AsyncSession, join_code: str
    ) -> QuizSession | None:
        stmt = (
            select(QuizSession)
            .where(QuizSession.join_code == join_code.strip().upper())
            .options(selectinload(QuizSession.participant))
        )
        result = await db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def count_questions(self, db: AsyncSession, quiz_sid: UUID) -> int:
        result = await db.execute(
            select(func.count(Question.sid)).where(Question.quiz_sid == quiz_sid)
        )
        return result.scalar_one()

    async def count_participant_answers(
        self, db: AsyncSession, participant_sid: UUID
    ) -> int:
        result = await db.execute(
            select(func.count(SessionAnswer.sid)).where(
                SessionAnswer.participant_sid == participant_sid
            )
        )
        return result.scalar_one()

    async def get_participant(
        self, db: AsyncSession, participant_sid: UUID
    ) -> SessionParticipant | None:
        return await self._get_participant(db, participant_sid)

    async def build_session_result(
        self, db: AsyncSession, session_sid: UUID
    ) -> dict[str, Any]:
        session = await self.get_session(db, session_sid)
        if not session:
            raise QuizSessionError("Session not found")
        total_questions = await self.count_questions(db, session.quiz_sid)
        return jsonable_encoder(
            {"session": session, "total_questions": total_questions}
        )

    async def build_quiz_snapshot(
        self, db: AsyncSession, quiz_sid: UUID, *, include_correct: bool = False
    ) -> dict[str, Any]:
        quiz = await self._get_quiz(db, quiz_sid)
        if not quiz:
            raise QuizSessionError("Quiz not found")

        questions = sorted(quiz.question, key=lambda question: question.order_num)
        return jsonable_encoder(
            {
                "sid": quiz.sid,
                "title": quiz.title,
                "description": quiz.description,
                "questions": [
                    {
                        "sid": question.sid,
                        "text": question.text,
                        "order_num": question.order_num,
                        "answer_options": [
                            {
                                "sid": option.sid,
                                "text": option.text,
                                **(
                                    {"is_correct": option.is_correct}
                                    if include_correct
                                    else {}
                                ),
                            }
                            for option in question.answer_option
                        ],
                    }
                    for question in questions
                ],
            }
        )

    async def _create_join_code(self, db: AsyncSession) -> str:
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = "".join(random.choice(alphabet) for _ in range(6))
            existing = await self.get_session_by_code(db, code)
            if not existing:
                return code

    async def _get_quiz(self, db: AsyncSession, quiz_sid: UUID) -> Quiz | None:
        stmt = (
            select(Quiz)
            .where(Quiz.sid == quiz_sid)
            .options(selectinload(Quiz.question).selectinload(Question.answer_option))
        )
        result = await db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def _get_participant(
        self, db: AsyncSession, participant_sid: UUID
    ) -> SessionParticipant | None:
        result = await db.execute(
            select(SessionParticipant).where(SessionParticipant.sid == participant_sid)
        )
        return result.scalar_one_or_none()

    async def _get_session_question(
        self, db: AsyncSession, quiz_sid: UUID, question_sid: UUID
    ) -> Question | None:
        result = await db.execute(
            select(Question).where(
                Question.sid == question_sid, Question.quiz_sid == quiz_sid
            )
        )
        return result.scalar_one_or_none()

    async def _get_question_option(
        self, db: AsyncSession, question_sid: UUID, answer_option_sid: UUID
    ) -> AnswerOption | None:
        result = await db.execute(
            select(AnswerOption).where(
                AnswerOption.sid == answer_option_sid,
                AnswerOption.question_sid == question_sid,
            )
        )
        return result.scalar_one_or_none()

    async def _get_existing_answer(
        self, db: AsyncSession, participant_sid: UUID, question_sid: UUID
    ) -> SessionAnswer | None:
        result = await db.execute(
            select(SessionAnswer).where(
                SessionAnswer.participant_sid == participant_sid,
                SessionAnswer.question_sid == question_sid,
            )
        )
        return result.scalar_one_or_none()


quiz_session_service = QuizSessionService()
