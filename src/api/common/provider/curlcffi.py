import asyncio
from collections.abc import AsyncIterator
from typing import Any, Mapping
from urllib import parse

import orjson
from curl_cffi import AsyncSession, BrowserTypeLiteral
from curl_cffi import Response as CurlCffiResponse
from curl_cffi.requests.errors import RequestsError

from src.api.common.provider import errors as err
from src.api.common.provider.base import AsyncProvider
from src.api.common.provider.middleware.base import RequestMiddlewareType
from src.api.common.provider.middleware.error import RequestErrorMiddleware
from src.api.common.provider.response import Response
from src.api.common.provider.types import RequestMethodType


class ClientResponseAdapter(Response):
    def __init__(self, origin_response: CurlCffiResponse, raw_content: bytes) -> None:
        self._origin_response = origin_response
        self._raw_content = raw_content

    async def __aenter__(self) -> "ClientResponseAdapter":
        return self

    async def __aexit__(self, *args: Any) -> None:
        self._origin_response.close()  # type: ignore

    async def json(self, **kwargs: Any) -> Any:
        encoding = kwargs.pop("encoding", "utf-8")
        stripped = self._raw_content.strip()
        return orjson.loads(stripped.decode(encoding), **kwargs)

    async def read(self) -> bytes:
        # returns it unchanged
        return self._raw_content

    async def text(self, **kwargs: Any) -> str:
        encoding, errors = (
            kwargs.get("encoding", "utf-8"),
            kwargs.get("errors", "strict"),
        )
        return self._raw_content.decode(encoding=encoding, errors=errors)

    @property
    def status(self) -> int:
        return self._origin_response.status_code

    @property
    def url(self) -> str:
        return str(self._origin_response.url)

    @property
    def headers(self) -> Mapping[str, Any]:
        return self._origin_response.headers

    @property
    def cookies(self) -> Mapping[str, Any]:
        return self._origin_response.cookies


class CurlCffiProvider(AsyncProvider):
    __slot__ = ("_session", "_kw")

    def __init__(
        self,
        url: str | None = None,
        middlewares: tuple[RequestMiddlewareType, ...] = (RequestErrorMiddleware(),),
    ) -> None:
        self._session: AsyncSession[CurlCffiResponse] | None = None
        self._kw: dict[str, Any] = {}
        super().__init__(url, middlewares)

    async def create_session(self) -> AsyncSession[CurlCffiResponse]:
        if self._session is None:
            max_clients = self._kw.pop("max_clients", 500)
            max_redirects = self._kw.pop("max_redirects", 3)
            impersonate: BrowserTypeLiteral = self._kw.pop("impersonate", "chrome120")
            self._session = AsyncSession(
                max_clients=max_clients,
                impersonate=impersonate,
                max_redirects=max_redirects,
                **self._kw,
            )
        return self._session

    async def close_session(self) -> None:
        if self._session is not None:
            await self._session.close()
            await asyncio.sleep(0.25)

    def _resolve_url(self, url_or_endpoint: str) -> str:
        if parse.urlparse(url_or_endpoint).scheme != "":
            url = url_or_endpoint
        else:
            if not self.url:
                raise ValueError("If you want to use endpoints you should provide url.")
            url = parse.urljoin(self.url, url_or_endpoint)

        return url

    async def make_request(
        self, method: RequestMethodType, url_or_endpoint: str = "", **kw: Any
    ) -> Response:
        session = await self.create_session()
        try:
            response: CurlCffiResponse = await session.request(
                method=method, url=self._resolve_url(url_or_endpoint), **kw
            )
            return ClientResponseAdapter(response, response.content)

        except TimeoutError as e:
            raise err.NetworkError("Request timeout error") from e
        except RequestsError as e:
            raise err.NetworkError(f"{type(e).__name__} occurred") from e

    def update_cookies(self, values: Mapping[str, Any]) -> None:
        if not self._session:
            raise TypeError("Cannot update headers while session is not connected")
        elif self._session and self._session._closed:
            raise TypeError("Cannot update headers while session disconnected")
        self._session.cookies.update(values)  # type: ignore

    def update_headers(self, values: Mapping[str, Any]) -> None:
        if not self._session:
            raise TypeError("Cannot update headers while session is not connected")
        elif self._session and self._session._closed:  # type: ignore
            raise TypeError("Cannot update headers while session disconnected")
        self._session.headers.update(values)

    async def stream_content(
        self,
        url_or_endpoint: str,
        chunk_size: int = 65536,
        raise_for_status: bool = True,
        **kw: Any,
    ) -> AsyncIterator[bytes]:
        session = await self.create_session()
        response = await session.get(url=self._resolve_url(url_or_endpoint), **kw)
        async for chunk in response.aiter_content(chunk_size):
            yield chunk
