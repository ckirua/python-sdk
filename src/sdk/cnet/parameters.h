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
#define PG_CONNECTION_PARAMETERS_CLASS_NAME "PGConnectionParameters"

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

// ---------------- PGConnectionParameters ----------------

typedef struct {
    AbstractSocketParametersObject base;
    // Dedicated fields for PG connection parameters (PyObject pointers first)
    PyObject *_user;
    PyObject *_password;
    PyObject *_database;
    PyObject *_driver;
    // OPTIMIZED: Single cache validation mechanism
    PyObject *_url_cache;
    Py_hash_t _combined_hash;  // Single hash instead of 6 separate hashes
    int _cache_generation;     // Increment when any field changes
} PGConnectionParametersObject;

// Inline utility functions for PGConnectionParameters
static inline void PGConnectionParameters_init_cache(PGConnectionParametersObject *self) {
    self->_url_cache = NULL;
    self->_combined_hash = -1; // Initialize combined hash
    self->_cache_generation = 0; // Initialize generation
    self->_user = NULL;
    self->_password = NULL;
    self->_database = NULL;
    self->_driver = NULL;
}

static inline void PGConnectionParameters_clear_cache(PGConnectionParametersObject *self) {
    Py_XDECREF(self->_url_cache);
    self->_url_cache = NULL;
    self->_combined_hash = -1; // Clear combined hash
    self->_cache_generation++; // Increment generation to invalidate cache
}

static inline void PGConnectionParameters_clear_fields(PGConnectionParametersObject *self) {
    Py_XDECREF(self->_user);
    Py_XDECREF(self->_password);
    Py_XDECREF(self->_database);
    Py_XDECREF(self->_driver);
    self->_user = NULL;
    self->_password = NULL;
    self->_database = NULL;
    self->_driver = NULL;
}

// OPTIMIZATION 2: Fast combined hash computation
static inline Py_hash_t compute_combined_hash(PyObject *host, PyObject *port, 
                                              PyObject *user, PyObject *password, 
                                              PyObject *database, PyObject *driver) {
    // Use pointer addresses for ultra-fast hashing since PyUnicode objects are immutable
    // This avoids expensive string hashing entirely
    Py_hash_t hash = 0;
    hash ^= (Py_hash_t)host;
    hash ^= (Py_hash_t)port << 1;
    hash ^= (Py_hash_t)user << 2;
    hash ^= (Py_hash_t)password << 3;
    hash ^= (Py_hash_t)database << 4;
    hash ^= (Py_hash_t)driver << 5;
    return hash;
}

// URL building utility functions for PGConnectionParameters
static inline PyObject *PGConnectionParameters_build_url(const char *driver_cstr, Py_ssize_t driver_len,
                                                        const char *user_cstr, Py_ssize_t user_len,
                                                        const char *password_cstr, Py_ssize_t password_len,
                                                        const char *host_cstr, Py_ssize_t host_len,
                                                        long port_val,
                                                        const char *database_cstr, Py_ssize_t database_len) {
    char portbuf[MAX_PORT_LENGTH];
    int portlen = snprintf(portbuf, sizeof(portbuf), "%ld", port_val >= 0 ? port_val : 0);
    
    if (portlen < 0 || portlen >= (int)sizeof(portbuf)) {
        PyErr_SetString(PyExc_ValueError, "Port value too large");
        return NULL;
    }

    // Precompute total length: driver + "://" + user + ":" + password + "@" + host + ":" + port + "/" + database
    size_t total_len = driver_len + 3 + user_len + 1 + password_len + 1 + host_len + 1 + portlen + 1 + database_len;

    // Allocate PyUnicode object directly (UTF-8, one-byte kind)
    PyObject *url_obj = PyUnicode_New(total_len, 127);
    if (!url_obj) return NULL;
    
    void *data = PyUnicode_DATA(url_obj);
    if (!data) {
        Py_DECREF(url_obj);
        return NULL;
    }

    // Copy bytes directly in sequence
    size_t offset = 0;
    memcpy((char *)data + offset, driver_cstr, driver_len);
    offset += driver_len;
    memcpy((char *)data + offset, "://", 3);
    offset += 3;
    memcpy((char *)data + offset, user_cstr, user_len);
    offset += user_len;
    ((char *)data)[offset] = ':';
    offset += 1;
    memcpy((char *)data + offset, password_cstr, password_len);
    offset += password_len;
    ((char *)data)[offset] = '@';
    offset += 1;
    memcpy((char *)data + offset, host_cstr, host_len);
    offset += host_len;
    ((char *)data)[offset] = ':';
    offset += 1;
    memcpy((char *)data + offset, portbuf, portlen);
    offset += portlen;
    ((char *)data)[offset] = '/';
    offset += 1;
    memcpy((char *)data + offset, database_cstr, database_len);

    // Set the length and ready the string
    if (PyUnicode_READY(url_obj) < 0) {
        Py_DECREF(url_obj);
        return NULL;
    }

    return url_obj;
}

// Function prototypes for PGConnectionParameters
static int PGConnectionParameters_init(PGConnectionParametersObject *self, PyObject *args, PyObject *kwds);
static void PGConnectionParameters_dealloc(PGConnectionParametersObject *self);
static PyObject *PGConnectionParameters_get_url(PGConnectionParametersObject *self, void *closure);

// Property getters and setters
static PyObject *PGConnectionParameters_get_host(PGConnectionParametersObject *self, void *closure);
static int PGConnectionParameters_set_host(PGConnectionParametersObject *self, PyObject *value, void *closure);
static PyObject *PGConnectionParameters_get_port(PGConnectionParametersObject *self, void *closure);
static int PGConnectionParameters_set_port(PGConnectionParametersObject *self, PyObject *value, void *closure);
static PyObject *PGConnectionParameters_get_user(PGConnectionParametersObject *self, void *closure);
static int PGConnectionParameters_set_user(PGConnectionParametersObject *self, PyObject *value, void *closure);
static PyObject *PGConnectionParameters_get_database(PGConnectionParametersObject *self, void *closure);
static int PGConnectionParameters_set_database(PGConnectionParametersObject *self, PyObject *value, void *closure);
static PyObject *PGConnectionParameters_get_driver(PGConnectionParametersObject *self, void *closure);
static int PGConnectionParameters_set_driver(PGConnectionParametersObject *self, PyObject *value, void *closure);
static int PGConnectionParameters_set_password(PGConnectionParametersObject *self, PyObject *value, void *closure);

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
