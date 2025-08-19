#!/usr/bin/env python3
"""
Basic examples of using different clock functions in ctime.
This example demonstrates the differences between various clock types,
their use cases, and practical timing examples.
"""
from datetime import datetime
from time import sleep

from sdk.ctime import (
    clock_monotonic,
    clock_monotonic_coarse,
    clock_monotonic_raw,
    clock_realtime,
    clock_realtime_coarse,
)


def format_ns(ns: int) -> str:
    """Format nanoseconds into a human-readable string with units."""
    if ns < 1_000:
        return f"{ns} ns"
    elif ns < 1_000_000:
        return f"{ns/1_000:.2f} µs"
    elif ns < 1_000_000_000:
        return f"{ns/1_000_000:.2f} ms"
    else:
        return f"{ns/1_000_000_000:.2f} s"


def demonstrate_clock_types():
    """Show the differences between various clock types with explanations."""
    print("=== Clock Types and Their Uses ===\n")

    # 1. Realtime Clocks
    print("1. Realtime Clocks (Wall Time)")
    print(
        "   These represent the actual system time, like what you see on a wall clock."
    )
    print("   Use these when you need the current time of day.\n")

    rt = clock_realtime()
    rt_coarse = clock_realtime_coarse()
    # Convert nanoseconds since epoch to datetime
    dt = datetime.fromtimestamp(rt / 1_000_000_000)

    print(f"   Current wall time: {dt.strftime('%Y-%m-%d %H:%M:%S.%f')}")
    print(f"   - Precise:  {rt:,} ns (higher resolution)")
    print(f"   - Coarse:   {rt_coarse:,} ns (lower resolution, faster)")
    print(
        f"   - Difference between precise and coarse: {format_ns(abs(rt - rt_coarse))}\n"
    )

    # 2. Monotonic Clocks
    print("2. Monotonic Clocks (Always Increasing)")
    print(
        "   These are guaranteed to never go backwards and are not affected by system"
    )
    print("   time changes. Ideal for measuring intervals and timeouts.\n")

    mono_raw = clock_monotonic_raw()
    mono = clock_monotonic()
    mono_coarse = clock_monotonic_coarse()

    print(f"   - Raw:      {mono_raw:,} ns (hardware-based, no NTP adjustments)")
    print(f"   - Normal:   {mono:,} ns (NTP adjusted)")
    print(f"   - Coarse:   {mono_coarse:,} ns (lower resolution, faster)")
    print(
        f"   - Difference between raw and normal: {format_ns(abs(mono_raw - mono))}\n"
    )


def demonstrate_timing():
    """Show practical timing measurements with different clocks."""
    print("=== Practical Timing Examples ===\n")

    # 1. High-precision interval measurement
    print("1. High-precision interval (using monotonic_raw)")
    start = clock_monotonic_raw()
    # Do some quick computation
    sum(range(1000))
    end = clock_monotonic_raw()
    print(f"   Quick computation took: {format_ns(end - start)}\n")

    # 2. Normal interval measurement
    print("2. Normal interval (using monotonic)")
    print("   Measuring a 1-second sleep:")
    start = clock_monotonic()
    sleep(1)
    end = clock_monotonic()
    duration = end - start
    print(f"   - Expected: 1.000000000 s")
    print(f"   - Actual:   {duration/1_000_000_000:.9f} s")
    print(f"   - Overhead: {format_ns(duration - 1_000_000_000)}\n")

    # 3. Coarse measurements
    print("3. Coarse measurements (using monotonic_coarse)")
    print("   Better performance but lower resolution:")
    start = clock_monotonic_coarse()
    sleep(0.1)  # Sleep for 100ms
    end = clock_monotonic_coarse()
    print(f"   100ms sleep measured as: {format_ns(end - start)}")
    print("   Note: Coarse clock might show less accurate measurements\n")


if __name__ == "__main__":
    demonstrate_clock_types()
    print("-" * 60 + "\n")
    demonstrate_timing()
