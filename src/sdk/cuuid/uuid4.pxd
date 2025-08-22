cdef extern from "uuid4.h":
    cdef void c_uuid4(unsigned char* uuid)
