

cdef class CyPGConnectionParameters:
    cdef str _url
    cdef dict _dict

    cpdef dict to_dict(self)
    cpdef str to_url(self)