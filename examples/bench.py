import timeit
from sdk.cnet import (
    FAbstractSocketParameters,
    FTCPSocketParameters,
    AbstractSocketParameters,
    TCPSocketParameters,
    PAbstractSocketParameters,
    PTCPSocketParameters,
)

def bench_fzmq_url_cached(n: int = 1_000_000):
    """Test FTCPSocketParameters.url property performance (C++/cython, cached)"""
    params = FTCPSocketParameters("127.0.0.1", 5555)
    def run():
        for _ in range(n):
            _ = params.url
    return timeit.timeit(run, number=1)

def bench_fzmq_url_no_cache(n: int = 1_000_000):
    """Test FTCPSocketParameters.url property performance with cache invalidation by creating new objects"""
    def run():
        for i in range(n):
            params = FTCPSocketParameters(f"127.0.0.{i % 256}", 5555 + (i % 1000))
            _ = params.url
    return timeit.timeit(run, number=1)

def bench_zmq_url_property(n: int = 1_000_000):
    """Test TCPSocketParameters.url property performance (Python)"""
    params = TCPSocketParameters("127.0.0.1", 5555)
    def run():
        for _ in range(n):
            _ = params.url
    return timeit.timeit(run, number=1)

def bench_zmq_url_str_conversion(n: int = 1_000_000):
    """Test string conversion of TCPSocketParameters.url property"""
    params = TCPSocketParameters("127.0.0.1", 5555)
    def run():
        for _ in range(n):
            _ = str(params.url)
    return timeit.timeit(run, number=1)

def bench_fzmq_url_mixed_cache(n: int = 1_000_000):
    """Test mixed cache hit/miss performance for FTCPSocketParameters.url"""
    def run():
        for i in range(n):
            if i % 100 == 0:
                params = FTCPSocketParameters(f"127.0.0.{i % 256}", 5555 + (i % 1000))
            else:
                params = FTCPSocketParameters("127.0.0.1", 5555)
            _ = params.url
    return timeit.timeit(run, number=1)

def bench_object_creation(n: int = 100_000):
    """Test FTCPSocketParameters object creation overhead"""
    def run():
        for _ in range(n):
            _ = FTCPSocketParameters("127.0.0.1", 5555)
    return timeit.timeit(run, number=1)

def bench_p_tcp_url_property(n: int = 1_000_000):
    """Test PTCPSocketParameters.url property performance (C, Python C API)"""
    params = PTCPSocketParameters("127.0.0.1", 5555)
    def run():
        for _ in range(n):
            _ = params.url
    return timeit.timeit(run, number=1)

def bench_p_tcp_url_str_conversion(n: int = 1_000_000):
    """Test string conversion of PTCPSocketParameters.url property (C, Python C API)"""
    params = PTCPSocketParameters("127.0.0.1", 5555)
    def run():
        for _ in range(n):
            _ = str(params.url)
    return timeit.timeit(run, number=1)

def bench_p_tcp_object_creation(n: int = 100_000):
    """Test PTCPSocketParameters object creation overhead (C, Python C API)"""
    def run():
        for _ in range(n):
            _ = PTCPSocketParameters("127.0.0.1", 5555)
    return timeit.timeit(run, number=1)

def main():
    N = 1_000_000
    print(f"Benchmarking with N={N} iterations")

    t1 = bench_fzmq_url_cached(N)
    print(f"FTCPSocketParameters.url (cached): {t1:.6f} sec")

    t2 = bench_fzmq_url_no_cache(N)
    print(f"FTCPSocketParameters.url (no cache): {t2:.6f} sec")

    t3 = bench_zmq_url_property(N)
    print(f"TCPSocketParameters.url (property): {t3:.6f} sec")

    t4 = bench_zmq_url_str_conversion(N)
    print(f"TCPSocketParameters.url (str conversion): {t4:.6f} sec")

    t5 = bench_fzmq_url_mixed_cache(N)
    print(f"FTCPSocketParameters.url (mixed cache): {t5:.6f} sec")

    N_obj = 100_000
    t6 = bench_object_creation(N_obj)
    print(f"FTCPSocketParameters object creation overhead ({N_obj} objects): {t6:.6f} sec")

    t7 = bench_p_tcp_url_property(N)
    print(f"PTCPSocketParameters.url (C API property): {t7:.6f} sec")

    t8 = bench_p_tcp_url_str_conversion(N)
    print(f"PTCPSocketParameters.url (C API str conversion): {t8:.6f} sec")

    t9 = bench_p_tcp_object_creation(N_obj)
    print(f"PTCPSocketParameters object creation overhead ({N_obj} objects, C API): {t9:.6f} sec")

    print(f"\nPerformance Analysis:")
    print(f"Cache speedup: {t2/t1:.1f}x")
    print(f"Property vs cached: {t3/t1:.1f}x")
    print(f"Mixed cache vs no-cache: {t2/t5:.1f}x")
    print(f"PTCPSocketParameters property vs FTCPSocketParameters cached: {t7/t1:.1f}x")
    print(f"PTCPSocketParameters str conversion vs FTCPSocketParameters cached: {t8/t1:.1f}x")
    print(f"PTCPSocketParameters object creation vs FTCPSocketParameters: {t9/t6:.1f}x")

if __name__ == "__main__":
    main()