from typing import List
from uuid import UUID

from fastapi import APIRouter, Path, HTTPException, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import repositories
from app import schemas
from app.core.deps.deps import get_db

router = APIRouter()


@router.get("", response_model=List[schemas.AnswerOptionInfo])
async def get_all_answer_options(db: AsyncSession = Depends(get_db)):
    res = await repositories.answer_option_repository.get_all(db)
    return res


@router.post("", response_model=schemas.AnswerOptionInfo)
async def create_answer_option(
    answer_option_data: schemas.AnswerOptionCreate, db: AsyncSession = Depends(get_db)
):
    return await repositories.answer_option_repository.create(db, answer_option_data)


@router.get("/{answer_option_sid}", response_model=schemas.AnswerOptionInfo)
async def get_answer_option_by_sid(
    answer_option_sid: UUID = Path(), db: AsyncSession = Depends(get_db)
):
    answer_option = repositories.answer_option_repository.get_by_sid(
        db, sid=answer_option_sid
    )
    if not answer_option:
        raise HTTPException(status_code=404, detail="Answer_option not found")

    return await answer_option


@router.put("/{answer_option_sid}", response_model=schemas.AnswerOptionBase)
async def update_answer_option(
    answer_option_sid: UUID = Path(),
    answer_option_data: schemas.AnswerOptionUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
):
    answer_option = await repositories.answer_option_repository.get_by_sid(
        db, sid=answer_option_sid
    )
    if not answer_option:
        raise HTTPException(status_code=404, detail="Answer option not found")

    return await repositories.answer_option_repository.update(
        db, db_obj=answer_option, obj_in=answer_option_data
    )


@router.delete("/{answer_option_sid}", status_code=204)
async def delete_answer_option(
    answer_option_sid: UUID = Path(), db: AsyncSession = Depends(get_db)
):
    answer_option = await repositories.answer_option_repository.get_by_sid(
        db, sid=answer_option_sid
    )
    if not answer_option:
        raise HTTPException(status_code=404, detail="Answer_option not found")

    await repositories.answer_option_repository.remove(db, sid=answer_option_sid)
    return None


@router.post("/delete_many", status_code=204)
async def delete_many_answer_optionzes(
    answer_option_sids: List[UUID] = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
):
    await repositories.answer_option_repository.remove_many(db, sids=answer_option_sids)
    return None
