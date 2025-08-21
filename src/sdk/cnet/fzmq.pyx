# distutils: language = c++
# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True

from libc.stdint cimport int32_t
from libcpp.string cimport string
from libcpp cimport bool

cdef extern from *:
    """
    #include <cstdio>
    """
    int snprintf(char *str, size_t size, const char *format, ...)

cdef class FAbstractSocketParameters:
    cdef public string _protocol
    cdef public string _host
    cdef public int32_t _port
    cdef public string _dir
    cdef public string _filename

    def __cinit__(self):
        self._protocol.clear()
        self._host.clear()
        self._port = -1
        self._dir.clear()
        self._filename.clear()

    @property
    def url(self):
        raise NotImplementedError("AbstractSocketParameters.url must be implemented by subclasses")


cdef class FTCPSocketParameters(FAbstractSocketParameters):
    cdef string _url_cache
    cdef bint _url_cache_valid

    def __cinit__(self, host: str, port: int):
        self._host = host.encode("utf-8")
        self._port = port
        self._protocol = "tcp"
        self._url_cache_valid = False
        self._url_cache.clear()

    cpdef void get_url(self):
        # Fast path: clear and preallocate only once, append in-place, avoid repeated size calculations
        self._url_cache.clear()
        cdef size_t proto_len = self._protocol.size()
        cdef size_t host_len = self._host.size()
        # "://" = 3, ":" = 1, max port = 6 (65535 + null), so reserve exact
        self._url_cache.reserve(proto_len + 3 + host_len + 1 + 6)
        self._url_cache.append(self._protocol)
        self._url_cache.append("://")
        self._url_cache.append(self._host)
        self._url_cache.append(":")
        # Use snprintf directly into a buffer, append only the used part
        cdef char portbuf[8]  # Enough for 65535 + null
        cdef int n = snprintf(portbuf, sizeof(portbuf), "%d", self._port)
        if n > 0:
            self._url_cache.append(portbuf, n)
        self._url_cache_valid = True
        
    @property
    def url(self):
        if not self._url_cache_valid:
            self.get_url()
        # Convert C++ string to Python str
        return self._url_cache.decode('utf-8')
