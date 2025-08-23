from typing import Dict


class PyPGConnectionParameters:
    """
    Connection parameters for PostgreSQL database.
    Provides both connection URL and dictionary formats.
    
    Optimized with __slots__ for reduced memory footprint.
    """
    __slots__ = ["_url", "_dict"]

    def __init__(self, host: str, port: int, user: str, password: str, database: str) -> None:
        # Format connection string once at initialization time
        self._url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        # Store parameters in dict for individual access
        self._dict = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }

    def to_dict(self) -> Dict[str, str | int]:
        """Return connection parameters as a dictionary."""
        return self._dict

    def to_url(self) -> str:
        """Return connection parameters as a PostgreSQL connection URL."""
        return self._url
    
    def __str__(self) -> str:
        """Return a sanitized string representation (no password)."""
        return f"PGConnectionParameters(host={self._dict['host']}, port={self._dict['port']}, user={self._dict['user']}, dbname={self._dict['dbname']})"
    
    def __repr__(self) -> str:
        """Return a sanitized string representation (no password)."""
        return self.__str__()

    @property
    def url(self) -> str:
        return self._url


cdef class CyPGConnectionParameters:
    def __cinit__(self, str host, int port, str user, str password, str database):
        self._url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self._dict = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }

    cpdef dict to_dict(self):
        return self._dict

    cpdef str to_url(self):
        return self._url

    def __str__(self):
        # Do not show password
        return f"PGConnectionParameters(host={self._dict['host']}, port={self._dict['port']}, user={self._dict['user']}, dbname={self._dict['database']})"

    def __repr__(self):
        return self.__str__()

    @property
    def url(self):
        return self._url

