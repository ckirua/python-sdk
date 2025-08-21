from typing import Any, Dict, Optional, Type, Awaitable

class HTTPMethods:
    GET: str
    POST: str
    PUT: str
    DELETE: str

class HTTPResponse:
    status_code: int
    headers: dict
    content: bytes
    ok: bool
    def __init__(self, status_code: int, headers: dict, content: bytes) -> None: ...

class HTTPRequest:
    url: str
    method: str
    headers: dict
    params: dict
    data: dict
    def __init__(
        self,
        url: str,
        method: str,
        headers: dict = ...,
        params: dict = ...,
        data: dict = ...,
    ) -> None: ...

class HTTPClient:
    def __init__(self) -> None: ...
    def connected(self) -> bool: ...
    async def __aenter__(
        self,
        connector: Any = ...,
        handle_cookies: bool = ...,
        verify_ssl: bool = ...,
        proxy: Any = ...,
    ) -> "HTTPClient": ...
    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[Exception],
        traceback: Optional[object],
    ) -> None: ...
    async def _request(
        self,
        url: str,
        method: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any: ...
    def connect(
        self,
        connector: Any = ...,
        handle_cookies: bool = ...,
        verify_ssl: bool = ...,
        proxy: Any = ...,
    ) -> None: ...
    async def disconnect(self) -> None: ...
    async def wait_connection(self, timeout: Optional[float] = ...) -> None: ...

def verify_http_status_code(status_code: int) -> bool: ...

