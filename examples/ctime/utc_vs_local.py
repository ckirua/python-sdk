#!/usr/bin/env python3
"""
Example showing both UTC and local time from clock_realtime.
"""
from datetime import UTC, datetime

from sdk.ctime import clock_realtime


def show_time_comparison():
    """Compare UTC and local time from the same timestamp."""
    print("=== UTC vs Local Time ===\n")

    # Get current time in nanoseconds since Unix epoch
    ns_since_epoch = clock_realtime()
    seconds_since_epoch = ns_since_epoch / 1_000_000_000

    # Convert to UTC and local time using modern approach
    utc_time = datetime.fromtimestamp(seconds_since_epoch, UTC)
    local_time = datetime.fromtimestamp(seconds_since_epoch)

    print("Current Time in Different Formats:")
    print("\n1. UTC (Coordinated Universal Time)")
    print(f"   Date:     {utc_time.strftime('%Y-%m-%d')}")
    print(f"   Time:     {utc_time.strftime('%H:%M:%S.%f')}")
    print(f"   Full:     {utc_time.strftime('%Y-%m-%d %H:%M:%S.%f')} UTC")
    print(f"   ISO:      {utc_time.isoformat()}")
    print(f"   Timezone: {utc_time.tzinfo}")

    print("\n2. Local Time")
    print(f"   Date:     {local_time.strftime('%Y-%m-%d')}")
    print(f"   Time:     {local_time.strftime('%H:%M:%S.%f')}")
    print(f"   Full:     {local_time.strftime('%Y-%m-%d %H:%M:%S.%f')} Local")
    print(f"   ISO:      {local_time.isoformat()}")
    print(f"   Timezone: {local_time.tzinfo}")

    # Show raw epoch values
    print("\n3. Raw Values")
    print(f"   Nanoseconds since Unix epoch:  {ns_since_epoch:,}")
    print(f"   Seconds since Unix epoch:      {seconds_since_epoch:,.3f}")


if __name__ == "__main__":
    show_time_comparison()
