#!/usr/bin/env python3
"""
Example demonstrating how to use clock_realtime to create and format dates and times.
Shows various datetime formatting options and calculations using ctime's realtime clock.
"""
from datetime import datetime, timedelta

from sdk.ctime import clock_realtime


def get_current_datetime():
    """Get current datetime from clock_realtime."""
    ns_since_epoch = clock_realtime()
    seconds_since_epoch = ns_since_epoch / 1_000_000_000
    return datetime.fromtimestamp(seconds_since_epoch)


def demonstrate_date_formats():
    """Show different ways to format dates."""
    print("=== Date Formatting ===\n")
    current_time = get_current_datetime()

    print("1. Basic Date Formats")
    print(f"   - YYYY-MM-DD:          {current_time.strftime('%Y-%m-%d')}")
    print(f"   - DD/MM/YYYY:          {current_time.strftime('%d/%m/%Y')}")
    print(f"   - Month DD, YYYY:      {current_time.strftime('%B %d, %Y')}")
    print(f"   - Abbreviated Month:    {current_time.strftime('%b %d, %Y')}")
    print(f"   - Year:                {current_time.strftime('%Y')}")
    print(f"   - Month (01-12):       {current_time.strftime('%m')}")
    print(f"   - Day (01-31):         {current_time.strftime('%d')}")
    print(f"   - Weekday:             {current_time.strftime('%A')}")
    print(f"   - Short Weekday:       {current_time.strftime('%a')}")
    print(f"   - Day of Year:         {current_time.strftime('%j')}\n")


def demonstrate_time_formats():
    """Show different ways to format times."""
    print("=== Time Formatting ===\n")
    current_time = get_current_datetime()

    print("1. Basic Time Components")
    print(f"   - Hour (24h):          {current_time.strftime('%H')}  (00-23)")
    print(f"   - Hour (12h):          {current_time.strftime('%I')}  (01-12)")
    print(f"   - AM/PM:               {current_time.strftime('%p')}")
    print(f"   - Minute:              {current_time.strftime('%M')}  (00-59)")
    print(f"   - Second:              {current_time.strftime('%S')}  (00-59)")
    print(f"   - Microsecond:         {current_time.strftime('%f')}\n")

    print("2. Combined Time Formats")
    print(f"   - 24-hour (HH:MM):     {current_time.strftime('%H:%M')}")
    print(f"   - 24-hour (HH:MM:SS):  {current_time.strftime('%H:%M:%S')}")
    print(f"   - 12-hour:             {current_time.strftime('%I:%M:%S %p')}")
    print(f"   - With microseconds:    {current_time.strftime('%H:%M:%S.%f')}\n")


def demonstrate_datetime_calculations():
    """Show calculations with datetime components."""
    print("=== DateTime Calculations ===\n")
    current_time = get_current_datetime()

    # Time adjustments
    in_2_hours = current_time + timedelta(hours=2)
    in_30_mins = current_time + timedelta(minutes=30)
    in_45_secs = current_time + timedelta(seconds=45)

    print("1. Time Adjustments")
    print(f"   Current time:          {current_time.strftime('%H:%M:%S')}")
    print(f"   In 2 hours:            {in_2_hours.strftime('%H:%M:%S')}")
    print(f"   In 30 minutes:         {in_30_mins.strftime('%H:%M:%S')}")
    print(f"   In 45 seconds:         {in_45_secs.strftime('%H:%M:%S')}\n")

    # Complex calculations
    future_time = current_time + timedelta(
        days=1, hours=2, minutes=30, seconds=15, microseconds=500000
    )

    print("2. Complex DateTime")
    print(f"   Current:     {current_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
    print(f"   Future:      {future_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")

    # Calculate difference
    diff = future_time - current_time
    print("\n3. Time Difference")
    print(f"   Total seconds:   {diff.total_seconds():.6f}")
    print(f"   Days:           {diff.days}")
    print(f"   Hours:          {diff.seconds // 3600}")
    print(f"   Minutes:        {(diff.seconds % 3600) // 60}")
    print(f"   Seconds:        {diff.seconds % 60}")
    print(f"   Microseconds:   {diff.microseconds}")


def demonstrate_timestamp_conversion():
    """Show conversions between different time representations."""
    print("\n=== Timestamp Conversions ===\n")

    ns_now = clock_realtime()
    current_time = datetime.fromtimestamp(ns_now / 1_000_000_000)

    print("1. Current Time Components:")
    print(f"   Date:        {current_time.strftime('%Y-%m-%d')}")
    print(f"   Time:        {current_time.strftime('%H:%M:%S.%f')}")
    print(f"   Timezone:    {current_time.strftime('%Z')}\n")

    print("2. Epoch Timestamps:")
    print(f"   Nanoseconds:   {ns_now:,} ns")
    print(f"   Milliseconds:  {ns_now // 1_000_000:,} ms")
    print(f"   Seconds:       {ns_now // 1_000_000_000:,} s")


if __name__ == "__main__":
    demonstrate_date_formats()
    demonstrate_time_formats()
    demonstrate_datetime_calculations()
    demonstrate_timestamp_conversion()
