from typing import Any

class AbstractSocketParameters:
    _protocol: str
    _host: str
    _port: int
    _dir: str
    _filename: str

    @property
    def url(self) -> str: ...
    

class TCPSocketParameters(AbstractSocketParameters):
    def __init__(self, host: str, port: int) -> None: ...
    @property
    def url(self) -> str: ...
