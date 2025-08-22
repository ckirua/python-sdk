import datetime
from sdk.ctime import rfc2822

# Example RFC2822 date strings (as bytes)
date_bytes = b"Fri, 22 Aug 2025 14:58:44 GMT"
date_bytes_tz = b"Fri, 22 Aug 2025 14:58:44 +0200"

# parse_rfc2822_bytes_to_timestamp
ts2 = rfc2822.parse_rfc2822_bytes_to_timestamp(date_bytes)
print("Bytes to timestamp:", ts2)

# parse_rfc2822_to_timestamp_with_tz
ts_tz = rfc2822.parse_rfc2822_bytes_to_timestamp_with_tz(date_bytes_tz)
print("Timestamp (with tz):", ts_tz)

# parse_rfc2822_bytes_to_datetime
dt = rfc2822.parse_rfc2822_bytes_to_datetime(date_bytes)
print("Bytes to datetime:", dt)

# parse_rfc2822_bytes_to_datetime with timezone
dt_tz = rfc2822.parse_rfc2822_bytes_to_datetime(date_bytes_tz)
print("Bytes to datetime (with tz):", dt_tz)
