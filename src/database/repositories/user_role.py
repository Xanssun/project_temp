import uuid
from collections.abc import Sequence
from typing import Iterable, Unpack

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as pg_insert

import src.database.models as models
from src.database.exceptions import EntityNotFoundError, InvalidParamsError
from src.database.repositories.base import BaseRepository
from src.database.repositories.types.user_role import CreateUserRoleType
from src.database.tools import on_integrity, select_with_relationships


class UserRoleRepository(BaseRepository[models.UserRole]):
    __slots__ = ()

    @property
    def model(self) -> type[models.UserRole]:
        return models.UserRole

    @on_integrity("user_uuid", "role_uuid")
    async def create(
        self, **data: Unpack[CreateUserRoleType]
    ) -> models.UserRole:
        return await self._crud.insert(**data)

    async def create_on_conflict_do_nothing(
        self, **data: Unpack[CreateUserRoleType]
    ) -> models.UserRole | None:
        stmt = (
            pg_insert(self.model)
            .on_conflict_do_nothing()
            .values(**data)
            .returning(self.model)
        )
        return (await self._session.execute(stmt)).scalars().first()

    async def select(
        self,
        uuid: uuid.UUID,
    ) -> models.UserRole | None:
        stmt = select_with_relationships(model=self.model).where(
            self.model.uuid == uuid
        )
        return (await self._session.scalars(stmt)).unique().first()

    async def get(self, uuid: uuid.UUID) -> models.UserRole:
        user_role = await self.select(uuid)
        if user_role is None:
            raise EntityNotFoundError("User role not found")
        return user_role

    @on_integrity("user_uuid", "role_uuid")
    async def create_many(
        self, data: Sequence[CreateUserRoleType]
    ) -> Sequence[models.UserRole]:
        return await self._crud.insert_many(data)

    async def select_many(
        self,
        user_uuid: uuid.UUID | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> tuple[int, Sequence[models.UserRole]]:
        where_clauses: list[sa.ColumnExpressionArgument[bool]] = []

        if user_uuid:
            where_clauses.append(self.model.user_uuid == user_uuid)

        total = await self._crud.count(*where_clauses)
        if total <= 0:
            return total, []

        stmt = (
            select_with_relationships(model=self.model)
            .where(*where_clauses)
            .offset(offset)
            .limit(limit)
        )

        results = (await self._session.scalars(stmt)).unique().all()

        return total, results

    async def delete(
        self,
        uuid: uuid.UUID | None = None,
        user_uuids: Iterable[uuid.UUID] | None = None,
        role_uuid: uuid.UUID | None = None,
    ) -> Sequence[models.UserRole]:
        if not any([uuid, user_uuids, role_uuid]):
            raise InvalidParamsError("at least one identifier must be provided")

        where_clauses: list[sa.ColumnExpressionArgument[bool]] = []

        if uuid:
            where_clauses.append(self.model.uuid == uuid)
        if user_uuids:
            where_clauses.append(self.model.user_uuid.in_(user_uuids))
        if role_uuid:
            where_clauses.append(self.model.role_uuid == role_uuid)

        result = await self._crud.delete(*where_clauses)
        return result
