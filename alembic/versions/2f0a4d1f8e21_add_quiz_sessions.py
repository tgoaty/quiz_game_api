"""add quiz sessions

Revision ID: 2f0a4d1f8e21
Revises: 9c6f48ade1f5
Create Date: 2026-05-02 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2f0a4d1f8e21"
down_revision: Union[str, None] = "9c6f48ade1f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quiz_session",
        sa.Column("quiz_sid", sa.UUID(), nullable=False, comment="Quiz ID"),
        sa.Column(
            "teacher_name",
            sa.String(),
            nullable=False,
            comment="Teacher display name",
        ),
        sa.Column(
            "join_code",
            sa.String(length=12),
            nullable=False,
            comment="Student join code",
        ),
        sa.Column(
            "status", sa.String(length=32), nullable=False, comment="Session status"
        ),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("sid", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["quiz_sid"], ["quizzes.quiz.sid"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("sid"),
        sa.UniqueConstraint("sid"),
        schema="quizzes",
        comment="Live quiz sessions",
    )
    op.create_index(
        op.f("ix_quizzes_quiz_session_join_code"),
        "quiz_session",
        ["join_code"],
        unique=True,
        schema="quizzes",
    )
    op.create_table(
        "session_participant",
        sa.Column("session_sid", sa.UUID(), nullable=False, comment="Session ID"),
        sa.Column(
            "name", sa.String(), nullable=False, comment="Participant display name"
        ),
        sa.Column(
            "score", sa.Integer(), nullable=False, comment="Correct answers count"
        ),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("sid", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_sid"], ["quizzes.quiz_session.sid"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("sid"),
        sa.UniqueConstraint("sid"),
        schema="quizzes",
        comment="Quiz session participants",
    )
    op.create_table(
        "session_answer",
        sa.Column(
            "participant_sid", sa.UUID(), nullable=False, comment="Participant ID"
        ),
        sa.Column("question_sid", sa.UUID(), nullable=False, comment="Question ID"),
        sa.Column(
            "answer_option_sid",
            sa.UUID(),
            nullable=False,
            comment="Answer option ID",
        ),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("sid", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["answer_option_sid"], ["quizzes.answer_option.sid"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["participant_sid"],
            ["quizzes.session_participant.sid"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["question_sid"], ["quizzes.question.sid"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("sid"),
        sa.UniqueConstraint(
            "participant_sid",
            "question_sid",
            name="uq_session_answer_participant_question",
        ),
        sa.UniqueConstraint("sid"),
        schema="quizzes",
        comment="Participant answers in quiz sessions",
    )


def downgrade() -> None:
    op.drop_table("session_answer", schema="quizzes")
    op.drop_table("session_participant", schema="quizzes")
    op.drop_index(
        op.f("ix_quizzes_quiz_session_join_code"),
        table_name="quiz_session",
        schema="quizzes",
    )
    op.drop_table("quiz_session", schema="quizzes")
