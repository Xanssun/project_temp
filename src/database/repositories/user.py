import uuid
from collections.abc import Sequence
from typing import Unpack

import sqlalchemy as sa

import src.database.models as models
from src.database.exceptions import EntityNotFoundError, InvalidParamsError
from src.database.models import types
from src.database.repositories.base import BaseRepository
from src.database.repositories.types import CreateUserType, UpdateUserType
from src.database.tools import on_integrity, select_with_relationships


class UserRepository(BaseRepository[models.User]):
    __slots__ = ()

    @property
    def model(self) -> type[models.User]:
        return models.User

    @on_integrity("login")
    async def create(self, **data: Unpack[CreateUserType]) -> models.User:
        return await self._crud.insert(**data)

    async def select(
        self,
        *loads: types._UserLoadsType,
        user_uuid: uuid.UUID | None = None,
        login: str | None = None,
        with_for_update: bool = False,
    ) -> models.User | None:
        if not any([user_uuid, login]):
            raise InvalidParamsError("at least one identifier must be provided")

        where_clauses: list[sa.ColumnExpressionArgument[bool]] = []

        if user_uuid:
            where_clauses.append(self.model.uuid == user_uuid)
        if login:
            where_clauses.append(self.model.login == login)

        stmt = select_with_relationships(*loads, model=self.model).where(*where_clauses)
        if with_for_update:
            stmt = stmt.with_for_update()
        return (await self._session.scalars(stmt)).unique().first()

    async def get(
        self,
        *loads: types._UserLoadsType,
        user_uuid: uuid.UUID | None = None,
        login: str | None = None,
        with_for_update: bool = False,
    ) -> models.User:
        user = await self.select(
            *loads,
            user_uuid=user_uuid,
            login=login,
            with_for_update=with_for_update,
        )
        if user is None:
            raise EntityNotFoundError("User not found")
        return user

    async def select_many(
        self,
        *loads: types._UserLoadsType,
        login: str | None = None,
        active: bool | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[int, Sequence[models.User]]:
        where_clauses: list[sa.ColumnExpressionArgument[bool]] = []

        if login:
            where_clauses.append(self.model.login == login)
        if active is not None:
            where_clauses.append(self.model.active == active)

        total = await self._crud.count(*where_clauses)
        if total <= 0:
            return total, []

        stmt = (
            select_with_relationships(*loads, model=self.model)
            .where(*where_clauses)
            .offset(offset)
            .limit(limit)
        )

        results = (await self._session.scalars(stmt)).unique().all()

        return total, results

    async def update(
        self,
        uuid: uuid.UUID,
        /,
        **data: Unpack[UpdateUserType],
    ) -> models.User:
        if not any([uuid]):
            raise InvalidParamsError("at least one identifier must be provided")

        result = await self._crud.update(self.model.uuid == uuid, **data)
        if not result:
            raise EntityNotFoundError("User not found")
        return result[0]

    async def delete(
        self, user_uuid: uuid.UUID | None = None, login: str | None = None
    ) -> models.User:
        if not any([user_uuid, login]):
            raise InvalidParamsError("at least one identifier must be provided")

        where_clauses: list[sa.ColumnExpressionArgument[bool]] = []

        if user_uuid:
            where_clauses.append(self.model.uuid == user_uuid)
        if login:
            where_clauses.append(self.model.login == login)

        result = await self._crud.delete(*where_clauses)
        if not result:
            raise EntityNotFoundError("User not found")
        return result[0]

    async def exists(
        self, user_uuid: uuid.UUID | None = None, login: str | None = None
    ) -> bool:
        if not any([user_uuid, login]):
            raise InvalidParamsError("at least one identifier must be provided")

        where_clauses: list[sa.ColumnExpressionArgument[bool]] = []

        if user_uuid:
            where_clauses.append(self.model.uuid == user_uuid)
        if login:
            where_clauses.append(self.model.login == login)

        return await self._crud.exists(*where_clauses)
