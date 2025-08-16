from typing import List
from uuid import UUID

from fastapi import APIRouter, Path, HTTPException, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import repositories
from app.core.deps.deps import get_db
from app import schemas

router = APIRouter()


@router.get("", response_model=List[schemas.QuestionInfo])
async def get_all_questions(db: AsyncSession = Depends(get_db)):
    res = await repositories.question_repository.get_all(db)
    return res


@router.post("", response_model=schemas.QuestionInfo)
async def create_question(
    question_data: schemas.QuestionCreate, db: AsyncSession = Depends(get_db)
):
    return await repositories.question_repository.create(db, question_data)


@router.get("/{question_sid}", response_model=schemas.QuestionInfo)
async def get_question_by_sid(
    question_sid: UUID = Path(), db: AsyncSession = Depends(get_db)
):
    question = repositories.question_repository.get_by_sid(db, sid=question_sid)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    return await question


@router.put("/{question_sid}", response_model=schemas.QuestionBase)
async def update_question(
    question_sid: UUID = Path(),
    question_data: schemas.QuestionUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
):
    question = await repositories.question_repository.get_by_sid(db, sid=question_sid)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    return await repositories.question_repository.update(
        db, db_obj=question, obj_in=question_data
    )


@router.delete("/{question_sid}", status_code=204)
async def delete_question(
    question_sid: UUID = Path(), db: AsyncSession = Depends(get_db)
):
    question = await repositories.question_repository.get_by_sid(db, sid=question_sid)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    await repositories.question_repository.remove(db, sid=question_sid)
    return None


@router.post("/delete_many", status_code=204)
async def delete_many_questionzes(
    question_sids: List[UUID] = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
):
    await repositories.question_repository.remove_many(db, sids=question_sids)
    return None
