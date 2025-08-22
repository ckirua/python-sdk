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

    return m;
}
