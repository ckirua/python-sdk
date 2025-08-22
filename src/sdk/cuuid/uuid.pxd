# cython: language_level=3

cimport cython
cimport cpython

from libc.stdint cimport uint8_t, int8_t
from libc.string cimport memcpy, memcmp

cdef extern from "Python.h":
    int PyUnicode_1BYTE_KIND
    const char* PyUnicode_AsUTF8AndSize(object unicode, Py_ssize_t *size) except NULL
    object PyUnicode_FromKindAndData(int kind, const void *buffer, Py_ssize_t size)
    object PyBytes_FromStringAndSize(const char *s, Py_ssize_t len)

cdef extern from "tohex.h":
    void uuid_to_str(const char *source, char *dest)
    void uuid_to_hex(const char *source, char *dest)

cdef extern from "uuid4.h":
    void c_uuid4(unsigned char* dest) nogil

cdef class __UUIDReplaceMe:
    pass

@cython.final
@cython.no_gc_clear
cdef class UUID(__UUIDReplaceMe):
    cdef char[16] _data
    cdef object _int
    cdef object _hash


cdef UUID uuid_from_buf(const char *buf)
cdef void uuid_bytes_from_str(str u, char *out)

cpdef bytes randstr_16()
cpdef UUID uuid4()
