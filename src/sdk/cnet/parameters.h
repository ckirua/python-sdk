#ifndef SDK_CNET_PARAMETERS_H
#define SDK_CNET_PARAMETERS_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include <stdio.h>
#include <string.h>

// ---------------- Constants and Macros ----------------

#define PARAMETERS_MODULE_NAME "sdk.cnet.parameters"
#define ABSTRACT_SOCKET_PARAMETERS_CLASS_NAME "AbstractSocketParameters"
#define TCP_SOCKET_PARAMETERS_CLASS_NAME "TCPSocketParameters"

// URL building constants
#define TCP_PROTOCOL "tcp"
#define URL_PREFIX "tcp://"
#define URL_SEPARATOR ":"
#define MAX_PORT_LENGTH 16

// Cache validation macros
#define CACHE_INVALID 0
#define CACHE_VALID 1

// ---------------- AbstractSocketParameters ----------------

typedef struct {
    PyObject_HEAD
    PyObject *_protocol;
    PyObject *_host;
    PyObject *_port;
    PyObject *_dir;
    PyObject *_filename;
} AbstractSocketParametersObject;

// Inline utility functions for AbstractSocketParameters
static inline void AbstractSocketParameters_init_fields(AbstractSocketParametersObject *self) {
    self->_protocol = NULL;
    self->_host = NULL;
    self->_port = NULL;
    self->_dir = NULL;
    self->_filename = NULL;
}

static inline void AbstractSocketParameters_clear_fields(AbstractSocketParametersObject *self) {
    Py_XDECREF(self->_protocol);
    Py_XDECREF(self->_host);
    Py_XDECREF(self->_port);
    Py_XDECREF(self->_dir);
    Py_XDECREF(self->_filename);
}

// Function prototypes for AbstractSocketParameters
static int AbstractSocketParameters_init(AbstractSocketParametersObject *self, PyObject *args, PyObject *kwds);
static void AbstractSocketParameters_dealloc(AbstractSocketParametersObject *self);
static PyObject *AbstractSocketParameters_get_url(AbstractSocketParametersObject *self, void *closure);

// ---------------- TCPSocketParameters ----------------

typedef struct {
    AbstractSocketParametersObject base;
    // For url optimization: cache the last url string and its components
    PyObject *_url_cache;      // PyUnicode object, NULL if invalid
    Py_hash_t _host_hash;
    long _port_val;
} TCPSocketParametersObject;

// Inline utility functions for TCPSocketParameters
static inline void TCPSocketParameters_init_cache(TCPSocketParametersObject *self) {
    self->_url_cache = NULL;
    self->_host_hash = -1;
    self->_port_val = -1;
}

static inline void TCPSocketParameters_clear_cache(TCPSocketParametersObject *self) {
    Py_XDECREF(self->_url_cache);
    self->_url_cache = NULL;
    self->_host_hash = -1;
    self->_port_val = -1;
}

static inline int TCPSocketParameters_is_cache_valid(TCPSocketParametersObject *self, Py_hash_t host_hash, long port_val) {
    return (self->_url_cache && 
            self->_host_hash == host_hash && 
            self->_port_val == port_val);
}

// URL building utility functions
static inline PyObject *TCPSocketParameters_build_url(const char *host_cstr, Py_ssize_t host_len, long port_val) {
    char portbuf[MAX_PORT_LENGTH];
    int portlen = snprintf(portbuf, sizeof(portbuf), "%ld", port_val >= 0 ? port_val : 0);
    
    if (portlen < 0 || portlen >= (int)sizeof(portbuf)) {
        PyErr_SetString(PyExc_ValueError, "Port value too large");
        return NULL;
    }

    // Precompute total length: "tcp://" + host + ":" + port
    static const char prefix[] = URL_PREFIX;
    size_t prefix_len = sizeof(prefix) - 1;
    size_t total_len = prefix_len + host_len + 1 + portlen;

    // Allocate PyUnicode object directly (UTF-8, one-byte kind)
    PyObject *url_obj = PyUnicode_New(total_len, 127);
    if (!url_obj) return NULL;
    
    void *data = PyUnicode_DATA(url_obj);
    if (!data) {
        Py_DECREF(url_obj);
        return NULL;
    }

    // Copy bytes directly
    memcpy(data, prefix, prefix_len);
    memcpy((char *)data + prefix_len, host_cstr, host_len);
    ((char *)data)[prefix_len + host_len] = ':';
    memcpy((char *)data + prefix_len + host_len + 1, portbuf, portlen);

    // Set the length and ready the string
    if (PyUnicode_READY(url_obj) < 0) {
        Py_DECREF(url_obj);
        return NULL;
    }

    return url_obj;
}

// Function prototypes for TCPSocketParameters
static int TCPSocketParameters_init(TCPSocketParametersObject *self, PyObject *args, PyObject *kwds);
static void TCPSocketParameters_dealloc(TCPSocketParametersObject *self);
static PyObject *TCPSocketParameters_get_url(TCPSocketParametersObject *self, void *closure);

// ---------------- Module Functions ----------------

// Module initialization function
PyMODINIT_FUNC PyInit_parameters(void);

// ---------------- Performance Optimization Macros ----------------

// Fast cache check macro
#define FAST_CACHE_CHECK(self, host_hash, port_val) \
    ((self)->_url_cache && (self)->_host_hash == (host_hash) && (self)->_port_val == (port_val))

// Safe field access macro
#define SAFE_FIELD_ACCESS(obj, field) \
    ((obj) && PyObject_CheckType((obj), &PyUnicode_Type) ? (obj) : NULL)

// Port value extraction macro
#define EXTRACT_PORT_VALUE(port_obj) \
    ((port_obj) && PyLong_Check(port_obj) ? PyLong_AsLong(port_obj) : 0)

#endif // SDK_CNET_PARAMETERS_H
