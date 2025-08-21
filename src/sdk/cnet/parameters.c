// Implementation of AbstractSocketParameters and TCPSocketParameters in raw C using Python C API

#include <Python.h>
#include <structmember.h>

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
    .tp_name = "cnet.AbstractSocketParameters",
    .tp_basicsize = sizeof(AbstractSocketParametersObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)AbstractSocketParameters_init,
    .tp_dealloc = (destructor)AbstractSocketParameters_dealloc,
    .tp_getset = AbstractSocketParameters_getset,
};

// ---------------- TCPSocketParameters ----------------

typedef struct {
    AbstractSocketParametersObject base;
} TCPSocketParametersObject;

static int
TCPSocketParameters_init(TCPSocketParametersObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *host = NULL;
    PyObject *port = NULL;
    static char *kwlist[] = {"host", "port", NULL};

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

    return 0;
}

static PyObject *
TCPSocketParameters_get_url(TCPSocketParametersObject *self, void *closure)
{
    // Return f"{self->_protocol}://{self->_host}:{self->_port}"
    PyObject *protocol = self->base._protocol;
    PyObject *host = self->base._host;
    PyObject *port = self->base._port;

    // Defensive: fallback to defaults if any are missing
    if (!protocol) {
        protocol = PyUnicode_FromString("tcp");
        if (!protocol) return NULL;
    } else {
        Py_INCREF(protocol);
    }
    if (!host) {
        host = PyUnicode_FromString("localhost");
        if (!host) {
            Py_DECREF(protocol);
            return NULL;
        }
    } else {
        Py_INCREF(host);
    }
    if (!port) {
        port = PyLong_FromLong(0);
        if (!port) {
            Py_DECREF(protocol);
            Py_DECREF(host);
            return NULL;
        }
    } else {
        Py_INCREF(port);
    }

    PyObject *port_str = PyObject_Str(port);
    if (!port_str) {
        Py_DECREF(protocol);
        Py_DECREF(host);
        Py_DECREF(port);
        return NULL;
    }

    // Use PyUnicode_Join for performance and to avoid format string issues
    // Build: [protocol, "://", host, ":", port_str]
    PyObject *sep = PyUnicode_New(0, 127); // empty separator
    if (!sep) {
        Py_DECREF(protocol);
        Py_DECREF(host);
        Py_DECREF(port);
        Py_DECREF(port_str);
        return NULL;
    }
    PyObject *parts = PyTuple_New(5);
    if (!parts) {
        Py_DECREF(protocol);
        Py_DECREF(host);
        Py_DECREF(port);
        Py_DECREF(port_str);
        Py_DECREF(sep);
        return NULL;
    }
    PyTuple_SET_ITEM(parts, 0, protocol); // steals ref
    PyTuple_SET_ITEM(parts, 1, PyUnicode_FromString("://")); // new ref
    PyTuple_SET_ITEM(parts, 2, host); // steals ref
    PyTuple_SET_ITEM(parts, 3, PyUnicode_FromString(":")); // new ref
    PyTuple_SET_ITEM(parts, 4, port_str); // steals ref

    PyObject *url = PyUnicode_Join(sep, parts);

    Py_DECREF(parts);
    Py_DECREF(sep);
    Py_DECREF(port); // Only port is not stolen by tuple

    return url;
}

static PyGetSetDef TCPSocketParameters_getset[] = {
    {"url", (getter)TCPSocketParameters_get_url, NULL, "url property", NULL},
    {NULL}
};

static PyTypeObject TCPSocketParametersType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "cnet.TCPSocketParameters",
    .tp_basicsize = sizeof(TCPSocketParametersObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_base = &AbstractSocketParametersType,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)TCPSocketParameters_init,
    .tp_getset = TCPSocketParameters_getset,
};

// ---------------- Module Init ----------------

static PyModuleDef parametersmodule = {
    PyModuleDef_HEAD_INIT,
    "parameters",
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
