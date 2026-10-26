from src.common.interfaces.gateway import BaseGateway
from src.database import DBGateway


class InternalServiceGateway(BaseGateway):
    __slots__ = ("database", "redis", "_settings")

    def __init__(
        self,
        database: DBGateway,
    ) -> None:
        self.database = database
        super().__init__(database)
