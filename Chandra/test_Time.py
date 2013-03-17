import Chandra.Time
from Chandra.Time import DateTime, convert
import unittest

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class TestConvert(unittest.TestCase):
    def test_mxDateTime_in(self):
        self.assertEqual(convert('1998-01-01 00:00:30'), 93.184)

    def test_mxDateTime_out(self):
        d = convert(93.184, fmt_out='mxDateTime')
        self.assertEqual(d.date, '1998-01-01')
        self.assertEqual(d.time, '00:00:30.00')

    def test_init_from_mxDateTime(self):
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

    def test_secs(self):
        self.assertEqual('%.3f' % DateTime(20483020.).secs, '20483020.000')
        self.assertEqual(DateTime(20483020.).date, '1998:238:01:42:36.816')
        self.assertEqual(DateTime('2012:001:00:00:00.000').secs, 441763266.18399996)
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

    def test_greta(self):
        self.assertEqual(DateTime('2007001.010203').date, '2007:001:01:02:03.000')
        self.assertEqual(DateTime('2007001.01020304').date, '2007:001:01:02:03.040')
        self.assertEqual(DateTime('2007:001:01:02:03.40').greta, '2007001.010203400')
        self.assertEqual(DateTime('2013055.000000000', format='greta').date, '2013:055:00:00:00.000')

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

if __name__ == '__main__':
    unittest.main()
