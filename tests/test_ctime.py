import platform
import time
import unittest
from datetime import datetime, timedelta

from sdk.ctime import (
    clock_monotonic,
    clock_monotonic_coarse,
    clock_monotonic_raw,
    clock_realtime,
    clock_realtime_coarse,
    datetime_range,
    strftime_range,
    ns_to_datetime,
    us_to_datetime,
    ms_to_datetime,
    s_to_datetime,
    datetime_to_ns,
    datetime_to_us,
    datetime_to_ms,
    datetime_to_s,
    change_ts_units,
    StrfTimeIterator,
    DateTimeIterator,
)


class TestClock(unittest.TestCase):
    def test_clock_monotonic_and_realtime(self):
        self.assertIsInstance(clock_monotonic(), int)
        self.assertIsInstance(clock_realtime(), int)
        self.assertGreater(clock_monotonic(), 0)
        self.assertGreater(clock_realtime(), 0)

    def test_monotonic_and_realtime_increasing(self):
        m1 = clock_monotonic()
        r1 = clock_realtime()
        time.sleep(0.001)
        m2 = clock_monotonic()
        r2 = clock_realtime()
        self.assertGreaterEqual(m2, m1)
        self.assertGreaterEqual(r2, r1)

    def test_nanosecond_scale(self):
        self.assertGreater(clock_realtime(), 1e18)
        self.assertGreater(clock_monotonic(), 1e9)

    @unittest.skipUnless(platform.system().lower() == "linux", "Linux-specific clocks")
    def test_linux_clocks(self):
        self.assertIsInstance(clock_monotonic_raw(), int)
        self.assertIsInstance(clock_monotonic_coarse(), int)
        self.assertIsInstance(clock_realtime_coarse(), int)
        self.assertGreater(clock_monotonic_raw(), 0)
        self.assertGreater(clock_monotonic_coarse(), 0)
        self.assertGreater(clock_realtime_coarse(), 0)

        raw1 = clock_monotonic_raw()
        coarse1 = clock_monotonic_coarse()
        realcoarse1 = clock_realtime_coarse()
        time.sleep(0.001)
        raw2 = clock_monotonic_raw()
        coarse2 = clock_monotonic_coarse()
        realcoarse2 = clock_realtime_coarse()
        self.assertGreaterEqual(raw2, raw1)
        self.assertGreaterEqual(coarse2, coarse1)
        self.assertGreaterEqual(realcoarse2, realcoarse1)

    def test_monotonic_consistency(self):
        vals = [clock_monotonic() for _ in range(5)]
        for i in range(1, 5):
            self.assertGreaterEqual(vals[i], vals[i - 1])

    def test_clock_speed(self):
        t0 = time.time()
        for _ in range(1000):
            clock_monotonic()
            clock_realtime()
        t1 = time.time()
        self.assertLess(t1 - t0, 1.0)


class TestRanges(unittest.TestCase):
    def test_datetime_range(self):
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 0, 0, 3)
        step = timedelta(seconds=1)
        result = datetime_range(start, end, step)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], start)
        self.assertEqual(result[-1], end)

    def test_strftime_range(self):
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 0, 0, 2)
        step = timedelta(seconds=1)
        fmt = "%H:%M:%S"
        result = strftime_range(start, end, step, fmt)
        self.assertEqual(result, ["00:00:00", "00:00:01", "00:00:02"])


class TestIterators(unittest.TestCase):
    def test_datetime_iterator(self):
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 0, 0, 2)
        step = timedelta(seconds=1)
        it = DateTimeIterator(start, end, step)
        result = list(it)
        self.assertEqual(result, [
            datetime(2024, 1, 1, 0, 0, 0),
            datetime(2024, 1, 1, 0, 0, 1),
            datetime(2024, 1, 1, 0, 0, 2),
        ])

    def test_strftime_iterator(self):
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 0, 0, 2)
        step = timedelta(seconds=1)
        fmt = "%H:%M:%S"
        it = StrfTimeIterator(start, end, step, fmt)
        result = list(it)
        self.assertEqual(result, ["00:00:00", "00:00:01", "00:00:02"])

    def test_strftime_iterator_default_format(self):
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 0, 0, 0)
        step = timedelta(seconds=1)
        it = StrfTimeIterator(start, end, step)
        result = list(it)
        self.assertEqual(result, [start.strftime("%Y-%m-%d %H:%M:%S")])


class TestConversions(unittest.TestCase):
    def setUp(self):
        # Use a fixed datetime for reproducibility
        self.dt = datetime(2024, 1, 1, 12, 34, 56, 789123)
        # Calculate expected timestamps
        self.s = int(self.dt.timestamp())
        self.ms = int(self.dt.timestamp() * 1_000)
        self.us = int(self.dt.timestamp() * 1_000_000)
        self.ns = int(self.dt.timestamp() * 1_000_000_000)

    def test_datetime_to_ns_and_back(self):
        ns = datetime_to_ns(self.dt)
        dt2 = ns_to_datetime(ns)
        # Allow for microsecond rounding
        self.assertAlmostEqual(self.dt.timestamp(), dt2.timestamp(), places=3)

    def test_datetime_to_us_and_back(self):
        us = datetime_to_us(self.dt)
        dt2 = us_to_datetime(us)
        self.assertAlmostEqual(self.dt.timestamp(), dt2.timestamp(), places=6)

    def test_datetime_to_ms_and_back(self):
        ms = datetime_to_ms(self.dt)
        dt2 = ms_to_datetime(ms)
        self.assertAlmostEqual(self.dt.timestamp(), dt2.timestamp(), places=3)

    def test_datetime_to_s_and_back(self):
        s = datetime_to_s(self.dt)
        dt2 = s_to_datetime(int(s))
        self.assertAlmostEqual(self.dt.replace(microsecond=0).timestamp(), dt2.timestamp(), places=0)

    def test_change_ts_units(self):
        # ns to us
        ns = 1704102896789123456
        us = change_ts_units(ns, from_unit="ns", to_unit="us")
        self.assertEqual(us, ns // 1000)
        # us to ms
        ms = change_ts_units(us, from_unit="us", to_unit="ms")
        self.assertEqual(ms, us // 1000)
        # ms to s
        s = change_ts_units(ms, from_unit="ms", to_unit="s")
        self.assertEqual(s, ms // 1000)
        # s to ns
        ns2 = change_ts_units(s, from_unit="s", to_unit="ns")
        self.assertEqual(ns2, s * 1_000_000_000)
        # identity
        self.assertEqual(change_ts_units(ns, from_unit="ns", to_unit="ns"), ns)
        # unsupported unit
        with self.assertRaises(ValueError):
            change_ts_units(ns, from_unit="foo", to_unit="ns")
        with self.assertRaises(ValueError):
            change_ts_units(ns, from_unit="ns", to_unit="bar")


if __name__ == "__main__":
    unittest.main()
