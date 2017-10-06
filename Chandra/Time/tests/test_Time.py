# Licensed under a 3-clause BSD style license - see LICENSE.rst
import Chandra.Time
from Chandra.Time import DateTime, convert, convert_vals, date2secs, secs2date
import unittest
import time

try:
    import mx.DateTime
    HAS_MX_DATETIME = True
except ImportError:
    HAS_MX_DATETIME = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class TestFastConvert(unittest.TestCase):
    def test_convert_vals_scalar(self):
        fmts = ['date', 'secs', 'jd', 'mjd', 'fits', 'caldate']
        vals = {fmt: getattr(DateTime('2012:001'), fmt) for fmt in fmts}
        for fmt_in in fmts:
            val = vals[fmt_in]
            for fmt_out in fmts:
                if fmt_in != fmt_out:
                    convert_val = convert_vals(val, fmt_in, fmt_out)
                    convert_back = convert_vals(convert_val, fmt_out, fmt_in)
                    if val != convert_back:
                        print(fmt_in, fmt_out, val, convert_back)
                    self.assertEqual(convert_val, getattr(DateTime(val, format=fmt_in), fmt_out))
                    self.assertEqual(val, convert_back)

    def test_convert_vals_array(self):
        fmts = ['date', 'secs', 'jd', 'mjd', 'fits', 'caldate']
        vals = {fmt: getattr(DateTime(['2012:001', '2000:001']), fmt) for fmt in fmts}
        for fmt_in in fmts:
            val = vals[fmt_in]
            for fmt_out in fmts:
                if fmt_in != fmt_out:
                    convert_val = convert_vals(val, fmt_in, fmt_out)
                    convert_back = convert_vals(convert_val, fmt_out, fmt_in)
                    self.assertTrue(np.all(val == convert_back))

    def test_date2secs(self):
        vals = DateTime(['2012:001', '2000:001'])
        self.assertTrue(np.all(date2secs(vals.date) == vals.secs))

    def test_secs2date(self):
        vals = DateTime(['2012:001', '2000:001'])
        self.assertTrue(np.all(secs2date(vals.secs) == vals.date))


class TestConvert(unittest.TestCase):
    def test_mxDateTime_in(self):
        self.assertEqual(convert('1998-01-01 00:00:30'), 93.184)

    def test_mxDateTime_out(self):
        if HAS_MX_DATETIME:
            d = convert(93.184, fmt_out='mxDateTime')
            self.assertEqual(d.date, '1998-01-01')
            self.assertEqual(d.time, '00:00:30.00')

    def test_init_from_mxDateTime(self):
        if HAS_MX_DATETIME:
            mxd = DateTime('1999-01-01 12:13:14').mxDateTime
            self.assertEqual(DateTime(mxd).fits, '1999-01-01T12:14:18.184')
            self.assertEqual(DateTime(mxd).mxDateTime.strftime('%c'),
                             'Fri Jan  1 12:13:14 1999')

    def test_iso(self):
        self.assertEqual(convert(93.184, fmt_out='iso'), '1998-01-01 00:00:30.000')
        self.assertEqual(convert(93.184, fmt_out='iso'), '1998-01-01 00:00:30.000')
        self.assertEqual(DateTime(93.184).iso,           '1998-01-01 00:00:30.000')
        self.assertEqual(DateTime('1998-01-01 00:00:30.000').secs, 93.184)
        self.assertEqual(DateTime('1998-01-01 00:00:30').secs, 93.184)
        self.assertEqual(DateTime('1998-1-1 0:0:1.111').secs, 64.295)

    def test_secs(self):
        self.assertEqual('%.3f' % DateTime(20483020.).secs, '20483020.000')
        self.assertEqual(DateTime(20483020.).date, '1998:238:01:42:36.816')
        self.assertAlmostEqual(DateTime('2012:001:00:00:00.000').secs, 441763266.18399996, places=2)
        self.assertEqual(DateTime(473385667.18399996).date, '2013:001:00:00:00.000')

    def test_fits2secs(self):
        self.assertEqual(convert('1998-01-01T00:00:30'), 30)

    def test_fits2unix(self):
        self.assertEqual(convert('1998-01-01T00:00:30', fmt_out='unix'), 883612766.816)
        self.assertEqual(convert('2007-01-01T00:00:00', fmt_out='unix'), 1167609534.816)
        self.assertEqual(DateTime('2007-01-01T00:00:00').unix, 1167609534.816)

    def test_jd(self):
        self.assertEqual(DateTime('2007-01-01T00:00:00').jd, 2454101.4992455561)

    def test_mjd(self):
        self.assertEqual(DateTime('2007-01-01T00:00:00').mjd, 54100.999245555999)
        self.assertEqual(DateTime('2012-01-01T00:00:00').mjd, 55926.999233981)
        self.assertEqual(DateTime('2013-01-01T00:00:00').mjd, 56292.999222407)

    def test_plotdate(self):
        """
        Validate against cxctime2plotdate and round-trip
        >>> cxctime2plotdate([DateTime('2010:001').secs])
        array([ 733773.5])
        """
        pd = DateTime('2010:001').plotdate
        self.assertEqual(pd, 733773.5)
        self.assertEqual(DateTime(pd, format='plotdate').date, '2010:001:12:00:00.000')

    def test_greta(self):
        self.assertEqual(DateTime('2007001.000000000').date, '2007:001:00:00:00.000')
        self.assertEqual(DateTime('2007001.0').date, '2007:001:00:00:00.000')
        self.assertEqual(DateTime(2007001.0).date, '2007:001:00:00:00.000')
        self.assertEqual(DateTime('2007001.010203').date, '2007:001:01:02:03.000')
        self.assertEqual(DateTime('2007001.01020304').date, '2007:001:01:02:03.040')
        self.assertEqual(DateTime('2007:001:01:02:03.40').greta, '2007001.010203400')
        self.assertEqual(DateTime('2007:001:00:00:00.000').greta, '2007001.000000000')

    def test_stop_day(self):
        self.assertEqual(DateTime('1996365.010203').day_end().iso, '1996-12-31 00:00:00.000')
        self.assertEqual(DateTime('1996366.010203').day_end().iso, '1997-01-01 00:00:00.000')

    def test_start_day(self):
        self.assertEqual(DateTime('1996365.010203').day_start().iso, '1996-12-30 00:00:00.000')
        self.assertEqual(DateTime('1996367.010203').day_start().iso, '1997-01-01 00:00:00.000')

    def test_year_doy(self):
        self.assertEqual(DateTime(20483020.0).year_doy, '1998:238')
        self.assertEqual(DateTime('2004:121').date, '2004:121:12:00:00.000')
        
    def test_year_mon_day(self):
        self.assertEqual(DateTime('2004:121').year_mon_day, '2004-04-30')
        self.assertEqual(DateTime('2007-01-01').date, '2007:001:12:00:00.000')

    def test_add(self):
        self.assertEqual((DateTime('2007-01-01') + 7).date, DateTime('2007-01-08').date)

    def test_add_array(self):
        if HAS_NUMPY:
            dates_in = DateTime(np.array(['2007-01-01',
                                          '2008-02-01']))
            dates_out = dates_in + np.array([3, 4])
            dates_exp = DateTime(np.array(['2007-01-04',
                                           '2008-02-05']))
            self.assertTrue(np.all(dates_out.date == dates_exp.date))

    def test_sub_days(self):
        self.assertEqual((DateTime('2007-01-08') - 7).date, DateTime('2007-01-01').date)

    def test_sub_datetimes(self):
        self.assertEqual(DateTime('2007-01-08') - DateTime('2007-01-01'), 7)

    def test_sub_datetimes_array(self):
        if HAS_NUMPY:
            dates_1 = DateTime(np.array(['2007-01-08',
                                         '2008-01-08']))
            dates_2 = DateTime(np.array(['2007-01-01',
                                         '2008-01-02']))
            delta_days = dates_1 - dates_2
            self.assertTrue(np.all(delta_days == np.array([7, 6])))

    def test_init_from_DateTime(self):
        date1 = DateTime('2001:001')
        date2 = DateTime(date1)
        self.assertEqual(date1.greta, date2.greta)

    def test_frac_year(self):
        date1 = DateTime('1999:170:01:02:03.232')
        date2 = DateTime(date1.frac_year, format='frac_year')
        self.assertEqual(date1.date, date2.date)
        date1 = DateTime('2001:180:00:00:00')
        self.assertAlmostEqual(date1.frac_year, 2001 + 179. / 365.)

    def test_leapsec_2015(self):
        """
        Tests for end of June 2015 leap second (PR #15).
        """
        # Test that there are 4 clock ticks where one usually expects 3
        t1 = DateTime('2015-06-30 23:59:59').secs
        t2 = DateTime('2015-07-01 00:00:02').secs
        self.assertAlmostEqual(t2 - t1, 4.0)
        # Test that a diff from a time before to the middle of the leap second is consistent
        t1 = DateTime('2015-06-30 23:59:59').secs
        t2 = DateTime('2015-06-30 23:59:60.5').secs
        self.assertAlmostEqual(t2 - t1, 1.5)
        # Test that a diff from the beginning of the leap second to the beginning of the next
        # day is no longer than a second
        t1 = DateTime('2015-06-30 23:59:60.').secs
        t2 = DateTime('2015-07-01 00:00:00').secs
        self.assertAlmostEqual(t2 - t1, 1.0)

    def test_leapsec_2016(self):
        """
        Tests for end of 2016 leap second. (PR #23).
        """
        # Test that there are 4 clock ticks where one usually expects 3
        t1 = DateTime('2016-12-31 23:59:59').secs
        t2 = DateTime('2017-01-01 00:00:02').secs
        self.assertAlmostEqual(t2 - t1, 4.0)
        # Test that a diff from a time before to the middle of the leap second is consistent
        t1 = DateTime('2016-12-31 23:59:59').secs
        t2 = DateTime('2016-12-31 23:59:60.5').secs
        self.assertAlmostEqual(t2 - t1, 1.5)
        # Test that a diff from the beginning of the leap second to the beginning of the year
        # is no longer than a second
        t1 = DateTime('2016-12-31 23:59:60.').secs
        t2 = DateTime('2017-01-01 00:00:00').secs
        self.assertAlmostEqual(t2 - t1, 1.0)

    def test_date_now(self):
        """
        Make sure that instantiating a DateTime object as NOW uses the
        the time at creation, not the time at attribute access.
        """
        date1 = DateTime()
        date1_date = date1.date
        time.sleep(1)
        self.assertEqual(date1.date, date1_date)

    def test_date_attributes(self):
        t = DateTime(['2015:160:02:24:01.250',
                      '2015:161:03:24:02.250',
                      '2015:162:04:24:03.250'])
        for attr, vals in (('year', np.array([2015, 2015, 2015])),
                           ('yday', np.array([160, 161, 162])),
                           ('hour', np.array([2, 3, 4])),
                           ('min', np.array([24, 24, 24])),
                           ('sec', np.array([1.25, 2.25, 3.25])),
                           ('mon', np.array([6, 6, 6])),
                           ('day', np.array([9, 10, 11])),
                           ('wday', np.array([1, 2, 3]))):
            self.assertTrue(np.all(getattr(t, attr) == vals))

        t = DateTime('2015:160:02:24:00.250')
        for attr, val in (('year', 2015),
                          ('yday', 160),
                          ('hour', 2),
                          ('min',  24),
                          ('sec',  0.25),
                          ('mon',  6),
                          ('day',  9),
                          ('wday', 1)):
            self.assertTrue(getattr(t, attr) == val)

if __name__ == '__main__':
    unittest.main()
