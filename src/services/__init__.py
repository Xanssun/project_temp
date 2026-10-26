from typing import Callable

from src.database.gateway import DBGateway

from .external.gateway import ExternalServiceGateway
from .internal.gateway import InternalServiceGateway

ServiceGatewayFactory = Callable[[], InternalServiceGateway]


def create_service_gateway_factory(
    database: Callable[[], DBGateway],
) -> ServiceGatewayFactory:
    def _create_instance() -> InternalServiceGateway:
        return InternalServiceGateway(database())

    return _create_instance


__all__ = (
    "InternalServiceGateway",
    "ExternalServiceGateway",
)
