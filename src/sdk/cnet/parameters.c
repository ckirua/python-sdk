// Implementation of AbstractSocketParameters and TCPSocketParameters in raw C using Python C API
// Optimized for low latency: minimize allocations, avoid PyUnicode_Join, use static buffers for url

// This file is a C extension for Python, implementing two classes:
//   - AbstractSocketParameters (abstract base)
//   - TCPSocketParameters (concrete, for TCP sockets)
// It is intended to be imported as sdk.cnet.parameters

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include <stdio.h>
#include <string.h>

// ---------------- AbstractSocketParameters ----------------

typedef struct {
    PyObject_HEAD
    PyObject *_protocol;
    PyObject *_host;
    PyObject *_port;
    PyObject *_dir;
    PyObject *_filename;
} AbstractSocketParametersObject;

static int
AbstractSocketParameters_init(AbstractSocketParametersObject *self, PyObject *args, PyObject *kwds)
{
    self->_protocol = NULL;
    self->_host = NULL;
    self->_port = NULL;
    self->_dir = NULL;
    self->_filename = NULL;
    return 0;
}

static void
AbstractSocketParameters_dealloc(AbstractSocketParametersObject *self)
{
    Py_XDECREF(self->_protocol);
    Py_XDECREF(self->_host);
    Py_XDECREF(self->_port);
    Py_XDECREF(self->_dir);
    Py_XDECREF(self->_filename);
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
    .tp_name = "sdk.cnet.parameters.AbstractSocketParameters",
    .tp_basicsize = sizeof(AbstractSocketParametersObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)AbstractSocketParameters_init,
    .tp_dealloc = (destructor)AbstractSocketParameters_dealloc,
    .tp_getset = AbstractSocketParameters_getset,
};

// ---------------- TCPSocketParameters ----------------

typedef struct {
    AbstractSocketParametersObject base;
    // For url optimization: cache the last url string and its components
    PyObject *_url_cache;      // PyUnicode object, NULL if invalid
    Py_hash_t _host_hash;
    long _port_val;
} TCPSocketParametersObject;

static int
TCPSocketParameters_init(TCPSocketParametersObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *host = NULL;
    PyObject *port = NULL;
    static char *kwlist[] = {"host", "port", NULL};

    // Invalidate url cache
    Py_XDECREF(self->_url_cache);
    self->_url_cache = NULL;
    self->_host_hash = -1;
    self->_port_val = -1;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist, &host, &port))
        return -1;

    Py_INCREF(host);
    Py_XDECREF(self->base._host);
    self->base._host = host;

    Py_INCREF(port);
    Py_XDECREF(self->base._port);
    self->base._port = port;

    PyObject *tcp_str = PyUnicode_FromString("tcp");
    if (!tcp_str) return -1;
    Py_XDECREF(self->base._protocol);
    self->base._protocol = tcp_str;

    Py_XDECREF(self->base._dir);
    self->base._dir = NULL;
    Py_XDECREF(self->base._filename);
    self->base._filename = NULL;

    // Invalidate url cache again (in case of re-init)
    Py_XDECREF(self->_url_cache);
    self->_url_cache = NULL;
    self->_host_hash = -1;
    self->_port_val = -1;

    return 0;
}

static void
TCPSocketParameters_dealloc(TCPSocketParametersObject *self)
{
    Py_XDECREF(self->_url_cache);
    AbstractSocketParameters_dealloc((AbstractSocketParametersObject *)self);
}

// Ultra-fast url property: cache, avoid repeated PyUnicode_AsUTF8, avoid snprintf if possible
static PyObject *
TCPSocketParameters_get_url(TCPSocketParametersObject *self, void *closure)
{
    // If cache is valid, return it
    PyObject *host = self->base._host;
    PyObject *port = self->base._port;

    // Compute hash of host and value of port
    Py_hash_t host_hash = -1;
    long port_val = -1;
    if (host && PyUnicode_Check(host)) {
        host_hash = PyObject_Hash(host);
        if (host_hash == -1 && PyErr_Occurred()) return NULL;
    }
    if (port && PyLong_Check(port)) {
        port_val = PyLong_AsLong(port);
        if (PyErr_Occurred()) return NULL;
    }

    if (self->_url_cache &&
        self->_host_hash == host_hash &&
        self->_port_val == port_val)
    {
        Py_INCREF(self->_url_cache);
        return self->_url_cache;
    }

    // Compose url: "tcp://<host>:<port>"
    // Note: host is NOT always "localhost". It is set by the user and can be any string.
    // If host is not provided, default to "localhost".
    const char *protocol_cstr = "tcp";
    const char *host_cstr = "localhost";
    char portbuf[16];
    Py_ssize_t host_len = 0;

    if (host && PyUnicode_Check(host)) {
        host_cstr = PyUnicode_AsUTF8AndSize(host, &host_len);
        if (!host_cstr) return NULL;
    } else {
        host_len = strlen(host_cstr);
    }

    int portlen = snprintf(portbuf, sizeof(portbuf), "%ld", port_val >= 0 ? port_val : 0);
    if (portlen < 0 || portlen >= (int)sizeof(portbuf)) {
        PyErr_SetString(PyExc_ValueError, "Port value too large");
        return NULL;
    }

    // Precompute total length: "tcp://" + host + ":" + port
    static const char prefix[] = "tcp://";
    size_t prefix_len = sizeof(prefix) - 1;
    size_t total_len = prefix_len + host_len + 1 + portlen;

    // Allocate PyUnicode object directly (UTF-8, one-byte kind)
    PyObject *url_obj = PyUnicode_New(total_len, 127);
    if (!url_obj) return NULL;
    void *data = PyUnicode_DATA(url_obj);

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

    // Cache the result
    Py_XDECREF(self->_url_cache);
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
    .tp_name = "sdk.cnet.parameters.TCPSocketParameters",
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
    "sdk.cnet.parameters",
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
    if (PyModule_AddObject(m, "AbstractSocketParameters", (PyObject *)&AbstractSocketParametersType) < 0) {
        Py_DECREF(&AbstractSocketParametersType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&TCPSocketParametersType);
    if (PyModule_AddObject(m, "TCPSocketParameters", (PyObject *)&TCPSocketParametersType) < 0) {
        Py_DECREF(&TCPSocketParametersType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
