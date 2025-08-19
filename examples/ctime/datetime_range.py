#!/usr/bin/env python3
"""
Example demonstrating the use of get_datetime_range from ctime.
This example shows how to generate datetime ranges with different intervals.
"""
from datetime import datetime, timedelta

from sdk.ctime import datetime_range


def demonstrate_basic_datetime_range():
    """Show basic datetime range usage."""
    print("Basic Datetime Range Example:\n")

    # Create a datetime range for the next 5 days
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=4)

    print(f"Datetimes from {start_date} to {end_date}:")
    for dt in datetime_range(start_date, end_date, step=timedelta(days=1)):
        print(f"  - {dt}")


def demonstrate_hourly_interval():
    """Show datetime range with hourly intervals."""
    print("\nHourly Interval Example:\n")

    # Create a datetime range with hourly intervals for a day
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)

    print(f"Hours from {start_date} to {end_date}:")
    for dt in datetime_range(start_date, end_date, step=timedelta(hours=1)):
        print(f"  - {dt.strftime('%Y-%m-%d %H:%M:%S')}")


def demonstrate_custom_interval():
    """Show datetime range with custom intervals."""
    print("\nCustom Interval Example (every 6 hours):\n")

    # Create a datetime range with 6-hour intervals
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=2)

    print(f"6-hour intervals from {start_date} to {end_date}:")
    for dt in datetime_range(start_date, end_date, step=timedelta(hours=6)):
        print(f"  - {dt.strftime('%Y-%m-%d %H:%M:%S')}")


def demonstrate_with_timezone():
    """Show datetime range with timezone information."""
    try:
        import zoneinfo

        print("\nTimezone Example:\n")

        # Create a datetime range with timezone
        timezone = zoneinfo.ZoneInfo("America/New_York")
        start_date = datetime.now(timezone).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_date = start_date + timedelta(days=1)

        print(f"4-hour intervals with timezone from {start_date} to {end_date}:")
        for dt in datetime_range(start_date, end_date, step=timedelta(hours=4)):
            print(f"  - {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    except ImportError:
        print("\nTimezone example skipped (zoneinfo module not available)")


if __name__ == "__main__":
    demonstrate_basic_datetime_range()
    demonstrate_hourly_interval()
    demonstrate_custom_interval()
    demonstrate_with_timezone()
