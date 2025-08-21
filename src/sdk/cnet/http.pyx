from typing import Any, Dict, Final, Literal, Optional
cimport cython
import aiosonic
import asyncio

DEF HTTP_OK_STATUS_CODE = 200
DEF HTTP_ERROR_STATUS_CODE = 300

cpdef inline bint verify_http_status_code(int status_code) noexcept nogil:
    return HTTP_OK_STATUS_CODE <= status_code < HTTP_ERROR_STATUS_CODE


@cython.final
cdef class HTTPMethods:
    GET: str = "GET"
    POST: str = "POST"
    PUT: str = "PUT"
    DELETE: str = "DELETE"


cdef class HTTPResponse:
    def __cinit__(self, int status_code, dict headers, bytes content):
        self.status_code = status_code
        self.headers = headers
        self.content = content
        self.ok = verify_http_status_code(status_code)


cdef class HTTPRequest:
    def __cinit__(
        self,
        str url,
        str method,
        dict headers=None,
        dict params=None,
        dict data=None,
    ):
        self.url = url
        self.method = method
        self.headers = headers
        self.params = params
        self.data = data

cdef class HTTPClient:
    cdef:
        object _session
        object _connection_event

    def __init__(self):
        self._session = None
        self._connection_event = asyncio.Event()

    cpdef bint connected(self):
        return self._connection_event.is_set()

    async def __aenter__(
        self,
        connector: Optional[aiosonic.TCPConnector] = None,
        handle_cookies: bool = False,
        verify_ssl: bool = True,
        proxy: Optional[aiosonic.Proxy] = None,
    ):
        self.connect(connector, handle_cookies, verify_ssl, proxy)
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[Exception],
        traceback: Optional[object],
    ) -> None:
        await self.disconnect()

    async def _request(
        self,
        url: str,
        method: str,
        *args,
        **kwargs: Any,
    ) -> aiosonic.HttpResponse:
        return await self._session.request(url, method, *args, **kwargs)

    cpdef void connect(
        self,
        connector: Optional[aiosonic.TCPConnector] = None,
        handle_cookies: bool = False,
        verify_ssl: bool = True,
        proxy: Optional[aiosonic.Proxy] = None,
    ):
        self._session = aiosonic.HTTPClient(
            connector=connector,
            handle_cookies=handle_cookies,
            verify_ssl=verify_ssl,
            proxy=proxy,
        )
        self._connection_event.set()

    async def disconnect(self):
        await self._session.connector.cleanup()
        self._session = None
        self._connection_event.clear()

    async def wait_connection(self, timeout: Optional[float] = None) -> None:
        await asyncio.wait_for(self._connection_event.wait(), timeout=timeout)

    async def request(self, request: HTTPRequest, *args: Any, **kwargs: Any) -> HTTPResponse:
        resp = await self._request(
            url=request.url,
            method=request.method,
            headers=request.headers,
            params=request.params,
            data=request.data,
        )
        return HTTPResponse(resp.status_code, dict(resp.headers), await resp.content())