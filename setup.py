import platform
import sys
import pybind11
from Cython.Build import cythonize
from setuptools import Extension, find_packages, setup


def get_build_dir():
    # Example: build/cython.linux-x86_64-cpython-313
    plat = platform.system().lower()
    machine = platform.machine().lower()
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"
    impl = platform.python_implementation().lower()
    # e.g. cpython-313
    py_tag = f"{impl}-{sys.version_info.major}{sys.version_info.minor}{sys.version_info.micro}"
    return f"build/cython.{plat}-{machine}-{py_tag}"


c_extensions = [
    Extension(
        "sdk.ctime.clock",
        ["src/sdk/ctime/clock.c"],
        extra_compile_args=[
            "-O3",
            "-march=native",
            "-Wno-unused-function",
            "-Wno-unused-variable",
        ],
        language="c",
    ),
    Extension(
        "sdk.ctime.iterators",
        ["src/sdk/ctime/iterators.c"],
        extra_compile_args=[
            "-O3",
            "-march=native",
            "-Wno-unused-function",
            "-Wno-unused-variable",
        ],
        language="c",
    ),
    Extension(
        "sdk.ctime.ranges",
        ["src/sdk/ctime/ranges.c"],
        extra_compile_args=[
            "-O3",
            "-march=native",
            "-Wno-unused-function",
            "-Wno-unused-variable",
        ],
        language="c",
    ),
]

cython_extensions = [
    Extension(
        "sdk.ctime.*",
        ["src/sdk/ctime/*.pyx"],
        extra_compile_args=[
            "-O3",
            "-march=native",
            "-Wno-unused-function",
            "-Wno-unused-variable",
        ],
        language="c",
    ),
    Extension(
        "sdk.cuuid.*",
        ["src/sdk/cuuid/*.pyx", "src/sdk/cuuid/uuid4.c"],
        extra_compile_args=[
            "-O2",
            "-march=native",
            "-Wno-unused-function",
            "-Wno-unused-variable",
        ],
        language="c",
    ),
        Extension(
        "sdk.cfs.*",
        ["src/sdk/cfs/*.pyx"],
        extra_compile_args=[
            "-O3",
            "-march=native",
            "-Wno-unused-function",
            "-Wno-unused-variable",
        ],
        language="c++",
    ),
]
pybind_extensions = [
    Extension(
        "sdk.cfs.zip",
        sources=["src/sdk/cfs/zip.cpp"],
        include_dirs=[pybind11.get_include()],
        libraries=["zip"],  # This is libzip, libzip.h not libzip.hpp
        language="c++",
        extra_compile_args=[
            "-O3",
            "-march=native",
            "-Wno-unused-function",
            "-Wno-unused-variable",
        ],
    )
]

if __name__ == "__main__":
    setup(
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        ext_modules=c_extensions
        + cythonize(
            cython_extensions,
            compiler_directives={
                "language_level": 3,
                "boundscheck": False,
                "wraparound": False,
                "cdivision": True,
                "infer_types": True,
                "nonecheck": False,  # Disable None checks for better performance
                "initializedcheck": False,  # Disable initialization checks
                "embedsignature": True,  # Keep function signatures for debugging
            },
            build_dir=get_build_dir(),
        ) + pybind_extensions,
    )
