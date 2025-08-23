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


class PGConnectionParameters(AbstractSocketParameters):
    def __init__(self, host: str, port: int, user: str, password: str, database: str, driver: str = "postgresql") -> None: ...
    
    # Properties for non-confidential attributes
    @property
    def host(self) -> str: ...
    
    @host.setter
    def host(self, value: str) -> None: ...
    
    @property
    def port(self) -> int: ...
    
    @port.setter
    def port(self, value: int) -> None: ...
    
    @property
    def user(self) -> str: ...
    
    @user.setter
    def user(self, value: str) -> None: ...
    
    @property
    def database(self) -> str: ...
    
    @database.setter
    def database(self, value: str) -> None: ...
    
    @property
    def driver(self) -> str: ...
    
    @driver.setter
    def driver(self, value: str) -> None: ...
    
    # Password can be set but not viewed (security)
    @property
    def password(self) -> str: ...
    
    @password.setter
    def password(self, value: str) -> None: ...
    
    @property
    def url(self) -> str: ...
