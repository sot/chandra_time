import Chandra.Time
from Chandra.Time import DateTime, convert
import unittest

class TestConvert(unittest.TestCase):
    def test_mxDateTime_in(self):
        self.assertEqual(convert('1998-01-01 00:00:30'), 93.184)

    def test_mxDateTime_out(self):
        d = convert(93.184, fmt_out='mxDateTime')
        self.assertEqual(d.date, '1998-01-01')
        self.assertEqual(d.time, '00:00:30.00')

    def test_iso(self):
        self.assertEqual(convert(93.184, fmt_out='iso'), '1998-01-01 00:00:30.000')
        self.assertEqual(convert(93.184, fmt_out='iso'), '1998-01-01 00:00:30.000')
        self.assertEqual(DateTime(93.184).iso,           '1998-01-01 00:00:30.000')
        self.assertEqual(DateTime('1998-01-01 00:00:30.000').secs, 93.184)
        self.assertEqual(DateTime('1998-01-01 00:00:30').secs, 93.184)

    def test_fits2secs(self):
        self.assertEqual(convert('1998-01-01T00:00:30'), 30)

    def test_fits2unix(self):
        self.assertEqual(convert('1998-01-01T00:00:30', fmt_out='unix'), 883612766.816)
        self.assertEqual(convert('2007-01-01T00:00:00', fmt_out='unix'), 1167609535.816)
        self.assertEqual(DateTime('2007-01-01T00:00:00').unix, 1167609535.816)

    def test_jd(self):
        self.assertEqual(DateTime('2007-01-01T00:00:00').jd, 2454101.499257130)

    def test_mjd(self):
        self.assertEqual(DateTime('2007-01-01T00:00:00').mjd, 54100.999257130)

    def test_greta(self):
        self.assertEqual(DateTime('2007001.010203').date, '2007:001:01:02:03.000')
        self.assertEqual(DateTime('2007001.01020304').date, '2007:001:01:02:03.040')
        self.assertEqual(DateTime('2007:001:01:02:03.40').greta, '2007001.010203400')

    def test_stop_day(self):
        self.assertEqual(DateTime('1996365.010203').day_end().iso, '1996-12-31 00:00:00.000')
        self.assertEqual(DateTime('1996366.010203').day_end().iso, '1997-01-01 00:00:00.000')

    def test_start_day(self):
        self.assertEqual(DateTime('1996365.010203').day_start().iso, '1996-12-30 00:00:00.000')
        self.assertEqual(DateTime('1996367.010203').day_start().iso, '1997-01-01 00:00:00.000')

if __name__ == '__main__':
    unittest.main()
