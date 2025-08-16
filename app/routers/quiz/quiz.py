from typing import List
from uuid import UUID

from fastapi import APIRouter, Path, HTTPException, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import repositories
from app.core.deps.deps import get_db
from app import schemas

router = APIRouter()


@router.get("", response_model=List[schemas.QuizInfo])
async def get_all_quizzies(db: AsyncSession = Depends(get_db)):
    res = await repositories.quiz_repository.get_all(db)
    return res


@router.post("", response_model=schemas.QuizInfo)
async def create_quiz(
    quiz_data: schemas.QuizCreate, db: AsyncSession = Depends(get_db)
):
    return await repositories.quiz_repository.create_with_relations(db, quiz_data)


@router.get("/{quiz_sid}", response_model=schemas.QuizInfo)
async def get_quiz_by_sid(quiz_sid: UUID = Path(), db: AsyncSession = Depends(get_db)):
    quiz = repositories.quiz_repository.get_by_sid(db, sid=quiz_sid)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return await quiz


@router.put("/{quiz_sid}", response_model=schemas.QuizBase)
async def update_quiz(
    quiz_sid: UUID = Path(),
    quiz_data: schemas.QuizUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
):
    quiz = await repositories.quiz_repository.get_by_sid(db, sid=quiz_sid)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return await repositories.quiz_repository.update(db, db_obj=quiz, obj_in=quiz_data)


@router.delete("/{quiz_sid}", status_code=204)
async def delete_quiz(quiz_sid: UUID = Path(), db: AsyncSession = Depends(get_db)):
    quiz = await repositories.quiz_repository.get_by_sid(db, sid=quiz_sid)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    await repositories.quiz_repository.remove(db, sid=quiz_sid)
    return None


@router.post("/delete_many", status_code=204)
async def delete_many_quizzes(
    quiz_sids: List[UUID] = Body(..., embed=True), db: AsyncSession = Depends(get_db)
):
    await repositories.quiz_repository.remove_many(db, sids=quiz_sids)
    return None
