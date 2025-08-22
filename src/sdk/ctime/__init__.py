import sys


if not sys.platform.startswith("win"):
    from .clock import (
        clock_monotonic_coarse,
        clock_monotonic_raw,
        clock_realtime_coarse,
    )
from .clock import (
    clock_monotonic,
    clock_realtime,
    clock_datetime,
)
from .conversions import (
    change_ts_units,
    datetime_to_ms,
    datetime_to_ns,
    datetime_to_s,
    datetime_to_us,
    ms_to_datetime,
    ns_to_datetime,
    s_to_datetime,
    us_to_datetime,
)
from .iterators import StrfTimeIterator, DateTimeIterator
from .ranges import datetime_range, strftime_range
from .rfc2822 import (
    parse_rfc2822_bytes_to_timestamp,
    parse_rfc2822_bytes_to_timestamp_with_tz,
    parse_rfc2822_bytes_to_datetime,
)

__all__ = (
    # clock.c
    "clock_monotonic",
    "clock_realtime",
    "clock_datetime",
    # iterator.c
    "DateTimeIterator",
    "StrfTimeIterator",
    # ranges.c
    "datetime_range",
    "strftime_range",
    # conversion.pyx
    "change_ts_units",
    "datetime_to_ms",
    "datetime_to_ns",
    "datetime_to_s",
    "datetime_to_us",
    "ms_to_datetime",
    "ns_to_datetime",
    "s_to_datetime",
    "us_to_datetime",
    # rfc2822.pyx
    "parse_rfc2822_bytes_to_timestamp",
    "parse_rfc2822_bytes_to_timestamp_with_tz",
    "parse_rfc2822_bytes_to_datetime",
)
if not sys.platform.startswith("win"):
    __all__ += (
        "clock_monotonic_coarse",
        "clock_monotonic_raw",
        "clock_realtime_coarse",
    )
