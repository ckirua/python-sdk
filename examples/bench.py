import timeit
import statistics
from sdk.cnet import (
    PGConnectionParameters,
    PyPGConnectionParameters,
    CyPGConnectionParameters,
)


def bench_pg_class(cls, n):
    """Benchmark creation and url access for a given class."""
    args = ("localhost", 5432, "user", "pass", "db")

    # Use globals to pass variables to timeit context, avoiding __main__ import issues
    globals_dict = {
        "cls": cls,
        "args": args,
    }

    # Time creation
    t_create = timeit.repeat(
        stmt="cls(*args)", 
        repeat=5, 
        number=n,
        globals=globals_dict,
    )
    # Time url access (fresh object each time)
    t_url = timeit.repeat(
        stmt="obj = cls(*args); _ = obj.url",
        repeat=5,
        number=n,
        globals=globals_dict,
    )
    # Time cached url access (reuse same object)
    obj = cls(*args)
    t_url_cached = timeit.repeat(
        stmt="_ = obj.url",
        repeat=5,
        number=n,
        globals={"obj": obj},
    )
    return {"create": t_create, "url": t_url, "url_cached": t_url_cached}


def print_stats(label, times, n):
    mean = statistics.mean(times)
    stdev = statistics.stdev(times)
    print(f"{label:18}: {mean*1e6/n:8.2f} μs/op (std {stdev*1e6/n:6.2f})")


def main():
    N = 100_000_0
    print(f"Benchmarking PGConnectionParameters classes with N={N} iterations\n")
    results = {}

    # Python class
    print("Testing PyPGConnectionParameters (pure Python)...")
    results["PyPG"] = bench_pg_class(PyPGConnectionParameters, N)
    # Cython cdef class
    print("Testing CyPGConnectionParameters (Cython cdef)...")
    results["CyPG"] = bench_pg_class(CyPGConnectionParameters, N)
    # Python class in parameters.py
    print("Testing PGConnectionParameters (Python)...")
    results["PG"] = bench_pg_class(PGConnectionParameters, N)

    print("\n=== Results (μs per operation) ===")
    for key, res in results.items():
        print(f"\n{key}:")
        print_stats("Create", res["create"], N)
        print_stats("URL (fresh)", res["url"], N)
        print_stats("URL (cached)", res["url_cached"], N)

    # Visualization
    import matplotlib.pyplot as plt

    labels = ["Create", "URL (fresh)", "URL (cached)"]
    classes = ["PG", "PyPG", "CyPG"]
    data = []
    for op in ["create", "url", "url_cached"]:
        row = []
        for cls in classes:
            row.append(statistics.mean(results[cls][op]) * 1e6 / N)
        data.append(row)
    x = range(len(labels))
    width = 0.25
    fig, ax = plt.subplots()
    for i, cls in enumerate(classes):
        ax.bar(
            [p + i * width for p in x],
            [data[j][i] for j in range(len(labels))],
            width,
            label=cls,
        )
    ax.set_xticks([p + width for p in x])
    ax.set_xticklabels(labels)
    ax.set_ylabel("μs per op")
    ax.set_title("PGConnectionParameters Benchmark")
    ax.legend()
    plt.tight_layout()
    plt.show()

    # Winner analysis
    print("\n=== Winner Analysis ===")
    for op, label in zip(["create", "url", "url_cached"], labels):
        best = min(classes, key=lambda c: statistics.mean(results[c][op]))
        print(f"{label:18}: {best} is fastest")
    

if __name__ == "__main__":
    main()