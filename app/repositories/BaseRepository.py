from typing import TypeVar, Generic, Type, Optional, List, Callable, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import DeclarativeMeta
from pydantic import BaseModel

TModel = TypeVar("TModel", bound=DeclarativeMeta)
TCreateSchema = TypeVar("TCreateSchema", bound=BaseModel)
TUpdateSchema = TypeVar("TUpdateSchema", bound=BaseModel)


class BaseRepository(Generic[TModel, TCreateSchema, TUpdateSchema]):
    def __init__(self, model: Type[TModel]):
        self.model = model

    async def get_by_sid(self, db: AsyncSession, sid: UUID) -> Optional[TModel]:
        stmt = select(self.model).where(self.model.sid == sid)
        result = await db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        *,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
    ) -> List[TModel]:
        stmt = select(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    stmt = stmt.where(getattr(self.model, field) == value)

        if order_by and hasattr(self.model, order_by):
            stmt = stmt.order_by(getattr(self.model, order_by))

        stmt = stmt.offset(skip).limit(limit)

        result = await db.execute(stmt)
        return result.unique().scalars().all()

    async def create(self, session: AsyncSession, schema: TCreateSchema) -> TModel:
        obj = self.model(**schema.model_dump())
        session.add(obj)
        await session.flush()
        return obj

    async def update(
        self, session: AsyncSession, db_obj: TModel, schema: TUpdateSchema
    ) -> TModel:
        for field, value in schema.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        await session.flush()
        return db_obj

    async def delete(self, session: AsyncSession, db_obj: TModel) -> None:
        await session.delete(db_obj)
        await session.flush()

    async def delete_many(
        self, session: AsyncSession, sids: List[UUID]
    ) -> Callable[[], int]:
        stmt = delete(self.model).where(self.model.sid.in_(sids))
        await session.execute(stmt)
        await session.flush()
