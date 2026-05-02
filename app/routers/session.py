from collections import defaultdict
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session_maker import AsyncSessionLocal
from app.core.deps.deps import get_db
from app.services.quiz_session import QuizSessionError, quiz_session_service

router = APIRouter()


class SessionConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()

    def attach(self, session_sid: UUID, websocket: WebSocket) -> None:
        self._connections[str(session_sid)].add(websocket)

    def detach(self, websocket: WebSocket) -> None:
        for sockets in self._connections.values():
            sockets.discard(websocket)

    async def send(self, websocket: WebSocket, event: str, payload: Any) -> None:
        await websocket.send_json(
            {"event": event, "payload": jsonable_encoder(payload)}
        )

    async def error(self, websocket: WebSocket, message: str) -> None:
        await self.send(websocket, "error", {"message": message})

    async def broadcast(self, session_sid: UUID, event: str, payload: Any) -> None:
        sockets = list(self._connections.get(str(session_sid), set()))
        for websocket in sockets:
            await self.send(websocket, event, payload)


manager = SessionConnectionManager()


@router.get("/{session_sid}/result")
async def get_session_result(
    session_sid: UUID, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    try:
        return await quiz_session_service.build_session_result(db, session_sid)
    except QuizSessionError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.websocket("/ws")
async def quiz_session_ws(websocket: WebSocket) -> None:
    await manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive_json()
            action = message.get("action")

            try:
                async with AsyncSessionLocal() as db:
                    if action == "create_session":
                        await _create_session(websocket, db, message)
                    elif action == "join_session":
                        await _join_session(websocket, db, message)
                    elif action == "start_session":
                        await _start_session(websocket, db, message)
                    elif action == "finish_session":
                        await _finish_session(websocket, db, message)
                    elif action == "submit_answer":
                        await _submit_answer(websocket, db, message)
                    elif action == "get_results":
                        await _get_results(websocket, db, message)
                    else:
                        await manager.error(websocket, "Unknown action")
            except (KeyError, TypeError, ValueError) as exc:
                await manager.error(websocket, f"Invalid payload: {exc}")
            except QuizSessionError as exc:
                await manager.error(websocket, str(exc))
    except WebSocketDisconnect:
        manager.detach(websocket)


async def _create_session(
    websocket: WebSocket, db: AsyncSession, message: dict[str, Any]
) -> None:
    session = await quiz_session_service.create_session(
        db,
        quiz_sid=UUID(message["quiz_sid"]),
        teacher_name=message["teacher_name"],
    )
    manager.attach(session.sid, websocket)
    quiz = await quiz_session_service.build_quiz_snapshot(
        db, session.quiz_sid, include_correct=True
    )
    await manager.send(
        websocket,
        "session_created",
        {"session": session, "quiz": quiz},
    )


async def _join_session(
    websocket: WebSocket, db: AsyncSession, message: dict[str, Any]
) -> None:
    participant = await quiz_session_service.join_session(
        db,
        join_code=message["join_code"],
        student_name=message["student_name"],
    )
    session = await quiz_session_service.get_session(db, participant.session_sid)
    if not session:
        raise QuizSessionError("Session not found")

    manager.attach(session.sid, websocket)
    quiz = await quiz_session_service.build_quiz_snapshot(db, session.quiz_sid)
    await manager.send(
        websocket,
        "joined",
        {"session": session, "participant": participant, "quiz": quiz},
    )
    await manager.broadcast(
        session.sid,
        "participant_joined",
        {"participant": participant, "participants_count": len(session.participant)},
    )


async def _start_session(
    websocket: WebSocket, db: AsyncSession, message: dict[str, Any]
) -> None:
    session = await quiz_session_service.start_session(db, UUID(message["session_sid"]))
    await manager.broadcast(session.sid, "session_started", {"session": session})


async def _finish_session(
    websocket: WebSocket, db: AsyncSession, message: dict[str, Any]
) -> None:
    session = await quiz_session_service.finish_session(
        db, UUID(message["session_sid"])
    )
    result = await quiz_session_service.build_session_result(db, session.sid)
    await manager.broadcast(session.sid, "session_finished", result)


async def _submit_answer(
    websocket: WebSocket, db: AsyncSession, message: dict[str, Any]
) -> None:
    answer = await quiz_session_service.submit_answer(
        db,
        participant_sid=UUID(message["participant_sid"]),
        question_sid=UUID(message["question_sid"]),
        answer_option_sid=UUID(message["answer_option_sid"]),
    )
    participant_sid = UUID(message["participant_sid"])
    await manager.send(websocket, "answer_saved", {"answer": answer})

    participant = await quiz_session_service.get_participant(db, participant_sid)
    if participant:
        await manager.broadcast(
            participant.session_sid,
            "participant_progress",
            {"participant": participant},
        )


async def _get_results(
    websocket: WebSocket, db: AsyncSession, message: dict[str, Any]
) -> None:
    result = await quiz_session_service.build_session_result(
        db, UUID(message["session_sid"])
    )
    await manager.send(websocket, "session_result", result)
