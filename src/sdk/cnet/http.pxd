cdef class HTTPRequest:
    cdef public str url
    cdef public str method
    cdef dict headers
    cdef dict params
    cdef dict data

cdef class HTTPResponse:
    cdef:
        public int status_code 
        public dict headers
        public bytes content   
        public bint ok  