// Implementation of AbstractSocketParameters and TCPSocketParameters in raw C using Python C API
// Optimized for low latency: minimize allocations, avoid PyUnicode_Join, use static buffers for url

// This file is a C extension for Python, implementing two classes:
//   - AbstractSocketParameters (abstract base)
//   - TCPSocketParameters (concrete, for TCP sockets)
// It is intended to be imported as sdk.cnet.parameters

#include "parameters.h"

// ---------------- AbstractSocketParameters ----------------

static int
AbstractSocketParameters_init(AbstractSocketParametersObject *self, PyObject *args, PyObject *kwds)
{
    AbstractSocketParameters_init_fields(self);
    return 0;
}

static void
AbstractSocketParameters_dealloc(AbstractSocketParametersObject *self)
{
    AbstractSocketParameters_clear_fields(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *
AbstractSocketParameters_get_url(AbstractSocketParametersObject *self, void *closure)
{
    PyErr_SetString(PyExc_NotImplementedError, "AbstractSocketParameters.url must be implemented by subclasses");
    return NULL;
}

static PyGetSetDef AbstractSocketParameters_getset[] = {
    {"url", (getter)AbstractSocketParameters_get_url, NULL, "url property", NULL},
    {NULL}
};

static PyTypeObject AbstractSocketParametersType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = PARAMETERS_MODULE_NAME "." ABSTRACT_SOCKET_PARAMETERS_CLASS_NAME,
    .tp_basicsize = sizeof(AbstractSocketParametersObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)AbstractSocketParameters_init,
    .tp_dealloc = (destructor)AbstractSocketParameters_dealloc,
    .tp_getset = AbstractSocketParameters_getset,
};

// ---------------- TCPSocketParameters ----------------

static int
TCPSocketParameters_init(TCPSocketParametersObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *host = NULL;
    PyObject *port = NULL;
    static char *kwlist[] = {"host", "port", NULL};

    // Initialize cache
    TCPSocketParameters_init_cache(self);

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist, &host, &port))
        return -1;

    Py_INCREF(host);
    self->base._host = host;

    Py_INCREF(port);
    self->base._port = port;

    PyObject *tcp_str = PyUnicode_FromString(TCP_PROTOCOL);
    if (!tcp_str) return -1;
    self->base._protocol = tcp_str;

    return 0;
}

static void
TCPSocketParameters_dealloc(TCPSocketParametersObject *self)
{
    TCPSocketParameters_clear_cache(self);
    AbstractSocketParameters_dealloc((AbstractSocketParametersObject *)self);
}

// Ultra-fast url property: cache, avoid repeated string generation
static PyObject *
TCPSocketParameters_get_url(TCPSocketParametersObject *self, void *closure)
{
    PyObject *host = self->base._host;
    PyObject *port = self->base._port;

    // Compute hash of host and value of port
    Py_hash_t host_hash = -1;
    long port_val = 0;
    
    if (host && PyUnicode_Check(host)) {
        host_hash = PyObject_Hash(host);
        if (host_hash == -1 && PyErr_Occurred()) return NULL;
    }
    
    if (port && PyLong_Check(port)) {
        port_val = PyLong_AsLong(port);
        if (PyErr_Occurred()) return NULL;
    }

    // Fast cache check using macro
    if (FAST_CACHE_CHECK(self, host_hash, port_val)) {
        Py_INCREF(self->_url_cache);
        return self->_url_cache;
    }

    // Get host string
    const char *host_cstr = "localhost";
    Py_ssize_t host_len = 0;
    
    if (host && PyUnicode_Check(host)) {
        host_cstr = PyUnicode_AsUTF8AndSize(host, &host_len);
        if (!host_cstr) return NULL;
    } else {
        host_len = strlen(host_cstr);
    }

    // Build URL using inline function from header
    PyObject *url_obj = TCPSocketParameters_build_url(host_cstr, host_len, port_val);
    if (!url_obj) return NULL;

    // Cache the result
    TCPSocketParameters_clear_cache(self);
    self->_url_cache = url_obj;
    Py_INCREF(url_obj);
    self->_host_hash = host_hash;
    self->_port_val = port_val;

    return url_obj;
}

static PyGetSetDef TCPSocketParameters_getset[] = {
    {"url", (getter)TCPSocketParameters_get_url, NULL, "url property", NULL},
    {NULL}
};

static PyTypeObject TCPSocketParametersType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = PARAMETERS_MODULE_NAME "." TCP_SOCKET_PARAMETERS_CLASS_NAME,
    .tp_basicsize = sizeof(TCPSocketParametersObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_base = &AbstractSocketParametersType,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)TCPSocketParameters_init,
    .tp_dealloc = (destructor)TCPSocketParameters_dealloc,
    .tp_getset = TCPSocketParameters_getset,
};

// ---------------- PGConnectionParameters ----------------

static int
PGConnectionParameters_init(PGConnectionParametersObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *host = NULL;
    PyObject *port = NULL;
    PyObject *user = NULL;
    PyObject *password = NULL;
    PyObject *database = NULL;
    PyObject *driver = NULL;
    static char *kwlist[] = {"host", "port", "user", "password", "database", "driver", NULL};

    // Initialize base struct fields
    AbstractSocketParameters_init_fields((AbstractSocketParametersObject *)self);
    
    // Initialize cache
    PGConnectionParameters_init_cache(self);

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOOOO|O", kwlist, &host, &port, &user, &password, &database, &driver))
        return -1;

    // Set default driver if not provided
    if (!driver) {
        driver = PyUnicode_FromString("postgresql");
        if (!driver) return -1;
    } else {
        Py_INCREF(driver);
    }

    Py_INCREF(host);
    self->base._host = host;

    Py_INCREF(port);
    self->base._port = port;

    Py_INCREF(user);
    self->_user = user;

    Py_INCREF(password);
    self->_password = password;

    Py_INCREF(database);
    self->_database = database;

    Py_INCREF(driver);
    self->_driver = driver;

    return 0;
}

static void
PGConnectionParameters_dealloc(PGConnectionParametersObject *self)
{
    PGConnectionParameters_clear_cache(self);
    PGConnectionParameters_clear_fields(self);
    AbstractSocketParameters_dealloc((AbstractSocketParametersObject *)self);
}

// Ultra-fast url property: cache, avoid repeated string generation
static PyObject *
PGConnectionParameters_get_url(PGConnectionParametersObject *self, void *closure)
{
    // Safety check: ensure all required fields are initialized
    if (!self->base._host || !self->base._port || !self->_user || !self->_password || !self->_database || !self->_driver) {
        PyErr_SetString(PyExc_RuntimeError, "PGConnectionParameters fields not properly initialized");
        return NULL;
    }

    PyObject *host = self->base._host;
    PyObject *port = self->base._port;
    PyObject *user = self->_user;
    PyObject *password = self->_password;
    PyObject *database = self->_database;
    PyObject *driver = self->_driver;

    // OPTIMIZATION 2: Ultra-fast pointer-based hashing (no expensive PyObject_Hash calls)
    Py_hash_t combined_hash = compute_combined_hash(host, port, user, password, database, driver);
    
    if (self->_url_cache && self->_combined_hash == combined_hash && self->_cache_generation == 0) {
        Py_INCREF(self->_url_cache);
        return self->_url_cache;
    }

    // Extract port value for URL construction (still needed)
    long port_val = 0;
    if (port && PyLong_Check(port)) {
        port_val = PyLong_AsLong(port);
        if (PyErr_Occurred()) return NULL;
    }

    // Get string representations
    const char *host_cstr = "localhost";
    const char *user_cstr = "";
    const char *password_cstr = "";
    const char *database_cstr = "";
    const char *driver_cstr = "postgresql";
    
    Py_ssize_t host_len = 0;
    Py_ssize_t user_len = 0;
    Py_ssize_t password_len = 0;
    Py_ssize_t database_len = 0;
    Py_ssize_t driver_len = 0;
    
    if (host && PyUnicode_Check(host)) {
        host_cstr = PyUnicode_AsUTF8AndSize(host, &host_len);
        if (!host_cstr) return NULL;
    } else {
        host_len = strlen(host_cstr);
    }
    
    if (user && PyUnicode_Check(user)) {
        user_cstr = PyUnicode_AsUTF8AndSize(user, &user_len);
        if (!user_cstr) return NULL;
    } else {
        user_len = strlen(user_cstr);
    }
    
    if (password && PyUnicode_Check(password)) {
        password_cstr = PyUnicode_AsUTF8AndSize(password, &password_len);
        if (!password_cstr) return NULL;
    } else {
        password_len = strlen(password_cstr);
    }
    
    if (database && PyUnicode_Check(database)) {
        database_cstr = PyUnicode_AsUTF8AndSize(database, &database_len);
        if (!database_cstr) return NULL;
    } else {
        database_len = strlen(database_cstr);
    }
    
    if (driver && PyUnicode_Check(driver)) {
        driver_cstr = PyUnicode_AsUTF8AndSize(driver, &driver_len);
        if (!driver_cstr) return NULL;
    } else {
        driver_len = strlen(driver_cstr);
    }

    // Build URL using inline function from header
    PyObject *url_obj = PGConnectionParameters_build_url(driver_cstr, driver_len, user_cstr, user_len,
                                                        password_cstr, password_len, host_cstr, host_len,
                                                        port_val, database_cstr, database_len);
    if (!url_obj) return NULL;

    // Cache the result
    PGConnectionParameters_clear_cache(self);
    self->_url_cache = url_obj;
    Py_INCREF(url_obj);
    self->_combined_hash = combined_hash; // Store combined hash
    self->_cache_generation = 0; // Reset generation

    return url_obj;
}

// Property getters and setters for PGConnectionParameters

static PyObject *
PGConnectionParameters_get_host(PGConnectionParametersObject *self, void *closure)
{
    if (self->base._host) {
        Py_INCREF(self->base._host);
        return self->base._host;
    }
    Py_RETURN_NONE;
}

static int
PGConnectionParameters_set_host(PGConnectionParametersObject *self, PyObject *value, void *closure)
{
    if (!value) {
        PyErr_SetString(PyExc_TypeError, "Cannot delete host attribute");
        return -1;
    }
    if (!PyUnicode_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "Host must be a string");
        return -1;
    }
    
    Py_XSETREF(self->base._host, value);
    Py_INCREF(value);
    
    // Invalidate cache since host changed
    self->_cache_generation++;
    
    return 0;
}

static PyObject *
PGConnectionParameters_get_port(PGConnectionParametersObject *self, void *closure)
{
    if (self->base._port) {
        Py_INCREF(self->base._port);
        return self->base._port;
    }
    Py_RETURN_NONE;
}

static int
PGConnectionParameters_set_port(PGConnectionParametersObject *self, PyObject *value, void *closure)
{
    if (!value) {
        PyErr_SetString(PyExc_TypeError, "Cannot delete port attribute");
        return -1;
    }
    if (!PyLong_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "Port must be an integer");
        return -1;
    }
    
    Py_XSETREF(self->base._port, value);
    Py_INCREF(value);
    
    // Invalidate cache since port changed
    self->_cache_generation++;
    
    return 0;
}

static PyObject *
PGConnectionParameters_get_user(PGConnectionParametersObject *self, void *closure)
{
    if (self->_user) {
        Py_INCREF(self->_user);
        return self->_user;
    }
    Py_RETURN_NONE;
}

static int
PGConnectionParameters_set_user(PGConnectionParametersObject *self, PyObject *value, void *closure)
{
    if (!value) {
        PyErr_SetString(PyExc_TypeError, "Cannot delete user attribute");
        return -1;
    }
    if (!PyUnicode_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "User must be a string");
        return -1;
    }
    
    Py_XSETREF(self->_user, value);
    Py_INCREF(value);
    
    // Invalidate cache since user changed
    self->_cache_generation++;
    
    return 0;
}

static PyObject *
PGConnectionParameters_get_database(PGConnectionParametersObject *self, void *closure)
{
    if (self->_database) {
        Py_INCREF(self->_database);
        return self->_database;
    }
    Py_RETURN_NONE;
}

static int
PGConnectionParameters_set_database(PGConnectionParametersObject *self, PyObject *value, void *closure)
{
    if (!value) {
        PyErr_SetString(PyExc_TypeError, "Cannot delete database attribute");
        return -1;
    }
    if (!PyUnicode_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "Database must be a string");
        return -1;
    }
    
    Py_XSETREF(self->_database, value);
    Py_INCREF(value);
    
    // Invalidate cache since database changed
    self->_cache_generation++;
    
    return 0;
}

static PyObject *
PGConnectionParameters_get_driver(PGConnectionParametersObject *self, void *closure)
{
    if (self->_driver) {
        Py_INCREF(self->_driver);
        return self->_driver;
    }
    Py_RETURN_NONE;
}

static int
PGConnectionParameters_set_driver(PGConnectionParametersObject *self, PyObject *value, void *closure)
{
    if (!value) {
        PyErr_SetString(PyExc_TypeError, "Cannot delete driver attribute");
        return -1;
    }
    if (!PyUnicode_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "Driver must be a string");
        return -1;
    }
    
    Py_XSETREF(self->_driver, value);
    Py_INCREF(value);
    
    // Invalidate cache since driver changed
    self->_cache_generation++;
    
    return 0;
}

static int
PGConnectionParameters_set_password(PGConnectionParametersObject *self, PyObject *value, void *closure)
{
    if (!value) {
        PyErr_SetString(PyExc_TypeError, "Cannot delete password attribute");
        return -1;
    }
    if (!PyUnicode_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "Password must be a string");
        return -1;
    }
    
    Py_XSETREF(self->_password, value);
    Py_INCREF(value);
    
    // Invalidate cache since password changed
    self->_cache_generation++;
    
    return 0;
}

static PyGetSetDef PGConnectionParameters_getset[] = {
    {"url", (getter)PGConnectionParameters_get_url, NULL, "url property", NULL},
    {"host", (getter)PGConnectionParameters_get_host, (setter)PGConnectionParameters_set_host, "host property", NULL},
    {"port", (getter)PGConnectionParameters_get_port, (setter)PGConnectionParameters_set_port, "port property", NULL},
    {"user", (getter)PGConnectionParameters_get_user, (setter)PGConnectionParameters_set_user, "user property", NULL},
    {"password", NULL, (setter)PGConnectionParameters_set_password, "password property (settable, not viewable)", NULL},
    {"database", (getter)PGConnectionParameters_get_database, (setter)PGConnectionParameters_set_database, "database property", NULL},
    {"driver", (getter)PGConnectionParameters_get_driver, (setter)PGConnectionParameters_set_driver, "driver property", NULL},
    {NULL}
};

static PyTypeObject PGConnectionParametersType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = PARAMETERS_MODULE_NAME "." PG_CONNECTION_PARAMETERS_CLASS_NAME,
    .tp_basicsize = sizeof(PGConnectionParametersObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_base = &AbstractSocketParametersType,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)PGConnectionParameters_init,
    .tp_dealloc = (destructor)PGConnectionParameters_dealloc,
    .tp_getset = PGConnectionParameters_getset,
};


// ---------------- Module Init ----------------

static PyModuleDef parametersmodule = {
    PyModuleDef_HEAD_INIT,
    PARAMETERS_MODULE_NAME,
    "C implementation of socket parameter classes",
    -1,
    NULL, NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit_parameters(void)
{
    PyObject *m;
    if (PyType_Ready(&AbstractSocketParametersType) < 0)
        return NULL;
    if (PyType_Ready(&TCPSocketParametersType) < 0)
        return NULL;
    if (PyType_Ready(&PGConnectionParametersType) < 0)
        return NULL;

    m = PyModule_Create(&parametersmodule);
    if (m == NULL)
        return NULL;

    Py_INCREF(&AbstractSocketParametersType);
    if (PyModule_AddObject(m, ABSTRACT_SOCKET_PARAMETERS_CLASS_NAME, (PyObject *)&AbstractSocketParametersType) < 0) {
        Py_DECREF(&AbstractSocketParametersType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&TCPSocketParametersType);
    if (PyModule_AddObject(m, TCP_SOCKET_PARAMETERS_CLASS_NAME, (PyObject *)&TCPSocketParametersType) < 0) {
        Py_DECREF(&TCPSocketParametersType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&PGConnectionParametersType);
    if (PyModule_AddObject(m, PG_CONNECTION_PARAMETERS_CLASS_NAME, (PyObject *)&PGConnectionParametersType) < 0) {
        Py_DECREF(&PGConnectionParametersType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
