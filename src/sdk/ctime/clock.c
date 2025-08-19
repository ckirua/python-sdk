#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <time.h>
#include <stdint.h>
#include <datetime.h>

// Constants and macros
#define NS_PER_SEC 1000000000ULL

// Compiler-specific noexcept equivalents - place BEFORE function name
#if defined(__GNUC__) || defined(__clang__)
    #define NOEXCEPT __attribute__((nothrow))
#elif defined(_MSC_VER)
    #define NOEXCEPT __declspec(nothrow)
#else
    #define NOEXCEPT
#endif

// The do { ... } while (0) pattern in this macro ensures that the macro behaves like a single statement.
// This allows it to be safely used in any context (such as inside if/else blocks) without causing unexpected behavior.
// The while(0) loop itself does not actually loop; the code inside the do { ... } block runs exactly once.
#define CLOCK_FUNC_NOGIL(clock_id) do { \
    struct timespec ts; \
    int err; \
    Py_BEGIN_ALLOW_THREADS \
    err = clock_gettime(clock_id, &ts); \
    Py_END_ALLOW_THREADS \
    if (err == -1) { \
        PyErr_SetFromErrno(PyExc_OSError); \
        return NULL; \
    } \
    return PyLong_FromUnsignedLongLong(((uint64_t)ts.tv_sec * NS_PER_SEC) + (uint64_t)ts.tv_nsec); \
} while (0)

// Inline helper for time conversion - attribute BEFORE function name
static inline NOEXCEPT uint64_t timespec_to_ns(const struct timespec *ts) {
    return ((uint64_t)ts->tv_sec * NS_PER_SEC) + (uint64_t)ts->tv_nsec;
}

// Clock functions - attribute BEFORE function name
static NOEXCEPT PyObject *c_clock_monotonic(PyObject *self, PyObject *args) { (void)self; (void)args; CLOCK_FUNC_NOGIL(CLOCK_MONOTONIC); }
static NOEXCEPT PyObject *c_clock_realtime(PyObject *self, PyObject *args) { (void)self; (void)args; CLOCK_FUNC_NOGIL(CLOCK_REALTIME); }
static NOEXCEPT PyObject *c_clock_monotonic_raw(PyObject *self, PyObject *args) { (void)self; (void)args; CLOCK_FUNC_NOGIL(CLOCK_MONOTONIC_RAW); }
static NOEXCEPT PyObject *c_clock_monotonic_coarse(PyObject *self, PyObject *args) { (void)self; (void)args; CLOCK_FUNC_NOGIL(CLOCK_MONOTONIC_COARSE); }
static NOEXCEPT PyObject *c_clock_realtime_coarse(PyObject *self, PyObject *args) { (void)self; (void)args; CLOCK_FUNC_NOGIL(CLOCK_REALTIME_COARSE); }

// Generic clock_gettime wrapper - attribute BEFORE function name
static NOEXCEPT PyObject *c_clock_generic(PyObject *self, PyObject *args, PyObject *kwargs) {
    (void)self;
    static char *keywords[] = {"clock_id", NULL};
    int clock_id;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "i", keywords, &clock_id))
        return NULL;

    struct timespec ts;
    int err;
    Py_BEGIN_ALLOW_THREADS
    err = clock_gettime(clock_id, &ts);
    Py_END_ALLOW_THREADS
    if (err == -1) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }
    return PyLong_FromUnsignedLongLong(timespec_to_ns(&ts));
}

// Function that returns datetime object from realtime clock - attribute BEFORE function name
static NOEXCEPT PyObject *c_clock_datetime(PyObject *self, PyObject *args) {
    (void)self; (void)args;
    
    struct timespec ts;
    int err;
    Py_BEGIN_ALLOW_THREADS
    err = clock_gettime(CLOCK_REALTIME, &ts);
    Py_END_ALLOW_THREADS
    if (err == -1) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }

    // Create datetime from timestamp
    PyObject *datetime_obj = PyDateTime_FromTimestamp(
        Py_BuildValue("(d)", (double)ts.tv_sec + (double)ts.tv_nsec / 1e9)
    );
    
    if (!datetime_obj) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create datetime object");
        return NULL;
    }
    
    return datetime_obj;
}

// Module methods: use c_* names directly in PyMethodDef
static PyMethodDef CTimeMethods[] = {
    {"clock_monotonic", c_clock_monotonic, METH_NOARGS, "Monotonic clock in nanoseconds"},
    {"clock_realtime", c_clock_realtime, METH_NOARGS, "Realtime since epoch in nanoseconds"},
    {"clock_monotonic_raw", c_clock_monotonic_raw, METH_NOARGS, "Raw monotonic clock in nanoseconds"},
    {"clock_monotonic_coarse", c_clock_monotonic_coarse, METH_NOARGS, "Coarse monotonic clock in nanoseconds"},
    {"clock_realtime_coarse", c_clock_realtime_coarse, METH_NOARGS, "Coarse realtime in nanoseconds"},
    {"clock_gettime", (PyCFunction)c_clock_generic, METH_VARARGS | METH_KEYWORDS,
     "Get time for specified clock_id in nanoseconds"},
    {"clock_datetime", c_clock_datetime, METH_NOARGS, "Realtime as datetime object"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef clock_module = {
    PyModuleDef_HEAD_INIT,
    "clock",
    "Low-level clock api",
    -1,
    CTimeMethods
};

// Module initialization - attribute BEFORE function name
NOEXCEPT PyMODINIT_FUNC PyInit_clock(void) {
    PyObject *module = PyModule_Create(&clock_module);
    if (!module) return NULL;

    // Initialize datetime C API
    PyDateTime_IMPORT;
    if (!PyDateTimeAPI) {
        PyErr_SetString(PyExc_ImportError, "Failed to import datetime C API");
        Py_DECREF(module);
        return NULL;
    }

    // Add clock constants
    PyModule_AddIntMacro(module, CLOCK_MONOTONIC);
    PyModule_AddIntMacro(module, CLOCK_REALTIME);
    PyModule_AddIntMacro(module, CLOCK_MONOTONIC_RAW);
    PyModule_AddIntMacro(module, CLOCK_MONOTONIC_COARSE);
    PyModule_AddIntMacro(module, CLOCK_REALTIME_COARSE);

    return module;
}