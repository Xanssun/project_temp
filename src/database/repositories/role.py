import uuid
from collections.abc import Sequence
from typing import Unpack

import sqlalchemy as sa

import src.database.models as models
from src.database.exceptions import EntityNotFoundError, InvalidParamsError
from src.database.models import types
from src.database.models.types import PermissionType
from src.database.repositories.base import BaseRepository
from src.database.repositories.types import CreateRoleType, UpdateRoleType
from src.database.tools import on_integrity, select_with_relationships


class RoleRepository(BaseRepository[models.Role]):
    __slots__ = ()

    @property
    def model(self) -> type[models.Role]:
        return models.Role

    @on_integrity("name")
    async def create(self, **data: Unpack[CreateRoleType]) -> models.Role:
        return await self._crud.insert(**data)

    async def select(
        self,
        *loads: types._RoleLoadsType,
        role_uuid: uuid.UUID | None = None,
        name: PermissionType | None = None,
    ) -> models.Role | None:
        if not any([role_uuid, name]):
            raise InvalidParamsError("at least one identifier must be provided")

        where_clauses: list[sa.ColumnExpressionArgument[bool]] = []

        if role_uuid:
            where_clauses.append(self.model.uuid == role_uuid)
        if name:
            where_clauses.append(self.model.name == name)

        stmt = select_with_relationships(*loads, model=self.model).where(*where_clauses)
        return (await self._session.scalars(stmt)).unique().first()

    async def get(
        self,
        *loads: types._RoleLoadsType,
        role_uuid: uuid.UUID | None = None,
        name: PermissionType | None = None,
    ) -> models.Role:
        role = await self.select(*loads, role_uuid=role_uuid, name=name)
        if role is None:
            raise EntityNotFoundError("Role not found")
        return role

    async def select_many(
        self,
        *loads: types._RoleLoadsType,
        names: list[PermissionType] | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[int, Sequence[models.Role]]:
        where_clauses: list[sa.ColumnExpressionArgument[bool]] = []

        if names is not None:
            where_clauses.append(self.model.name.in_(names))

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
        role_uuid: uuid.UUID,
        /,
        **data: Unpack[UpdateRoleType],
    ) -> models.Role:
        if not any([role_uuid]):
            raise InvalidParamsError("at least one identifier must be provided")

        result = await self._crud.update(self.model.uuid == role_uuid, **data)

        if not result:
            raise EntityNotFoundError("Role not found")
        return result[0]

    async def delete(
        self,
        role_uuid: uuid.UUID | None = None,
    ) -> models.Role:
        if not any([role_uuid]):
            raise InvalidParamsError("at least one identifier must be provided")

        where_clauses: list[sa.ColumnExpressionArgument[bool]] = []

        if role_uuid:
            where_clauses.append(self.model.uuid == role_uuid)

        result = await self._crud.delete(*where_clauses)
        if not result:
            raise EntityNotFoundError("Role not found")
        return result[0]
