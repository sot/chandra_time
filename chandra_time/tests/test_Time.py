# Licensed under a 3-clause BSD style license - see LICENSE.rst

import time
import numpy as np
import pytest

from ..Time import (
    DateTime,
    convert,
    convert_vals,
    date2secs,
    secs2date,
    use_noon_day_start,
    ChandraTimeError,
)
from cxotime import CxoTime
from astropy.time import Time


def test_convert_vals_scalar():
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
                assert convert_val == getattr(DateTime(val, format=fmt_in), fmt_out)
                assert val == convert_back


def test_convert_vals_array():
    fmts = ['date', 'secs', 'jd', 'mjd', 'fits', 'caldate']
    vals = {fmt: getattr(DateTime(['2012:001', '2000:001']), fmt) for fmt in fmts}
    for fmt_in in fmts:
        val = vals[fmt_in]
        for fmt_out in fmts:
            if fmt_in != fmt_out:
                convert_val = convert_vals(val, fmt_in, fmt_out)
                convert_back = convert_vals(convert_val, fmt_out, fmt_in)
                assert np.all(val == convert_back)


@pytest.mark.parametrize('date_in', ('2012:001:00:00:00',
                                     ['2012:001:00:00:00', '2000:001:00:00:00']))
def test_date2secs(date_in):
    vals = DateTime(date_in)
    assert np.all(date2secs(date_in) == vals.secs)
    if isinstance(date_in, str):
        date_in_bytes = date_in.encode('ascii')
    else:
        date_in_bytes = [date.encode('ascii') for date in date_in]
    assert np.all(date2secs(date_in_bytes) == vals.secs)


def test_secs2date():
    vals = DateTime(['2012:001', '2000:001'])
    assert np.all(secs2date(vals.secs) == vals.date)


def test_mxDateTime_in():
    assert convert('1998-01-01 00:00:30') == 93.184


def test_use_noon_day_start():
    from .. import Time
    assert Time._DAY_START == '00:00:00'
    use_noon_day_start()
    assert Time._DAY_START == '12:00:00'
    tm = DateTime('2020:001')
    assert tm.date == '2020:001:12:00:00.000'

    # Set it back for rest of testing
    Time._DAY_START = '00:00:00'


def test_iso():
    assert convert(93.184, fmt_out='iso') == '1998-01-01 00:00:30.000'
    assert convert(93.184, fmt_out='iso') == '1998-01-01 00:00:30.000'
    assert DateTime(93.184).iso == '1998-01-01 00:00:30.000'
    assert DateTime('1998-01-01 00:00:30.000').secs == 93.184
    assert DateTime('1998-01-01 00:00:30').secs == 93.184
    assert DateTime('1998-1-1 0:0:1.111').secs == 64.295


def test_secs():
    assert '%.3f' % DateTime(20483020.).secs == '20483020.000'
    assert DateTime(20483020.).date == '1998:238:01:42:36.816'
    assert np.isclose(DateTime('2012:001:00:00:00.000').secs, 441763266.18399996)
    assert DateTime(473385667.18399996).date == '2013:001:00:00:00.000'


def test_fits2secs():
    assert convert('1998-01-01T00:00:30') == 30


def test_fits2unix():
    assert convert('1998-01-01T00:00:30', fmt_out='unix') == 883612766.816
    assert convert('2007-01-01T00:00:00', fmt_out='unix') == 1167609534.816
    assert DateTime('2007-01-01T00:00:00').unix == 1167609534.816


def test_jd():
    assert DateTime('2007-01-01T00:00:00').jd == 2454101.4992455561


def test_mjd():
    assert DateTime('2007-01-01T00:00:00').mjd == 54100.999245555999
    assert DateTime('2012-01-01T00:00:00').mjd == 55926.999233981
    assert DateTime('2013-01-01T00:00:00').mjd == 56292.999222407


@pytest.mark.parametrize('time_cls', [Time, CxoTime])
@pytest.mark.parametrize('time_fmt', ['isot', 'unix', 'cxcsec'])
def test_init_from_astropy_time_scalar(time_cls, time_fmt):
    date = '1998:001:00:00:01.234'
    ct = time_cls(date)
    ct.format = time_fmt

    # Initialize DateTime from Time/CxoTime and convert to date or secs
    dt = DateTime(ct)
    assert dt.date == date
    assert np.isclose(dt.secs, ct.cxcsec)

    # Requesting .cxotime from DateTime initialized from CxoTime gives
    # back the original object.
    ct2 = dt.cxotime
    assert isinstance(ct2, CxoTime)
    assert ct2.date == date


def test_convert_to_cxotime_scalar():
    # Initialize DateTime from a date string and convert to CxoTime
    date = '1998:001:00:00:01.234'
    dt = DateTime(date)
    ct = dt.cxotime
    assert isinstance(ct, CxoTime)
    assert ct.date == date
    assert np.isclose(dt.secs, ct.secs)


@pytest.mark.parametrize('time_cls', [Time, CxoTime])
@pytest.mark.parametrize('time_fmt', ['isot', 'unix', 'cxcsec'])
def test_init_from_astropy_time_array(time_cls, time_fmt):
    dates = ['1998:001:00:00:01.234', '2000:001:01:02:03.456']
    ct = time_cls(dates)
    ct.format = time_fmt

    # Initialize DateTime from Time/CxoTime and convert to date or secs
    dt = DateTime(ct)
    assert np.all(dt.date == dates)
    assert np.allclose(dt.secs, ct.cxcsec)

    # Requesting .cxotime from DateTime initialized from CxoTime gives
    # back the original object.
    ct2 = dt.cxotime
    assert isinstance(ct2, CxoTime)
    assert np.all(ct2.date == dates)


def test_convert_to_cxotime_array():
    # Initialize DateTime from a date string and convert to CxoTime
    dates = ['1998:001:00:00:01.234', '2000:001:01:02:03.456']
    dt = DateTime(dates)
    ct = dt.cxotime
    assert isinstance(ct, CxoTime)
    assert np.all(ct.date == dates)
    assert np.allclose(dt.secs, ct.secs)


def test_plotdate():
    """Validate against cxctime2plotdate and round-trip
    >>> cxctime2plotdate([DateTime('2010:001').secs])
    array([ 733773.5])
    """
    pd = DateTime('2010:001').plotdate
    assert pd == 733773.0
    assert DateTime(pd, format='plotdate').date == '2010:001:00:00:00.000'


def test_greta():
    assert DateTime('2007001.000000000').date == '2007:001:00:00:00.000'
    assert DateTime('2007001.0').date == '2007:001:00:00:00.000'
    assert DateTime(2007001.0).date == '2007:001:00:00:00.000'
    assert DateTime('2007001.010203').date == '2007:001:01:02:03.000'
    assert DateTime('2007001.01020304').date == '2007:001:01:02:03.040'
    assert DateTime('2007:001:01:02:03.40').greta == '2007001.010203400'
    assert DateTime('2007:001:00:00:00.000').greta == '2007001.000000000'


def test_stop_day():
    assert DateTime('1996365.010203').day_end().iso == '1996-12-31 00:00:00.000'
    assert DateTime('1996366.010203').day_end().iso == '1997-01-01 00:00:00.000'


def test_start_day():
    assert DateTime('1996365.010203').day_start().iso == '1996-12-30 00:00:00.000'
    assert DateTime('1996367.010203').day_start().iso == '1997-01-01 00:00:00.000'


def test_year_doy():
    assert DateTime(20483020.0).year_doy == '1998:238'
    assert DateTime('2004:121').date == '2004:121:00:00:00.000'


def test_year_mon_day():
    assert DateTime('2004:121').year_mon_day == '2004-04-30'
    assert DateTime('2007-01-01').date == '2007:001:00:00:00.000'


def test_add():
    assert (DateTime('2007-01-01') + 7).date == DateTime('2007-01-08').date


def test_add_array():
    dates_in = DateTime(np.array(['2007-01-01', '2008-02-01']))
    dates_out = dates_in + np.array([3, 4])
    dates_exp = DateTime(np.array(['2007-01-04', '2008-02-05']))
    assert np.all(dates_out.date == dates_exp.date)


def test_sub_days():
    assert (DateTime('2007-01-08') - 7).date == DateTime('2007-01-01').date


def test_sub_datetimes():
    assert DateTime('2007-01-08') - DateTime('2007-01-01') == 7


def test_sub_datetimes_array():
    dates_1 = DateTime(np.array(['2007-01-08', '2008-01-08']))
    dates_2 = DateTime(np.array(['2007-01-01', '2008-01-02']))
    delta_days = dates_1 - dates_2
    assert np.all(delta_days == np.array([7, 6]))


def test_init_from_DateTime():
    date1 = DateTime('2001:001')
    date2 = DateTime(date1)
    assert date1.greta == date2.greta


def test_frac_year():
    date1 = DateTime('1999:170:01:02:03.232')
    date2 = DateTime(date1.frac_year, format='frac_year')
    assert date1.date == date2.date
    date1 = DateTime('2001:180:00:00:00')
    assert np.isclose(date1.frac_year, 2001 + 179. / 365.)


def test_leapsec_2015():
    """
    Tests for end of June 2015 leap second (PR #15).
    """
    # Test that there are 4 clock ticks where one usually expects 3
    t1 = DateTime('2015-06-30 23:59:59').secs
    t2 = DateTime('2015-07-01 00:00:02').secs
    np.isclose(t2 - t1, 4.0)
    # Test that a diff from a time before to the middle of the leap second is consistent
    t1 = DateTime('2015-06-30 23:59:59').secs
    t2 = DateTime('2015-06-30 23:59:60.5').secs
    np.isclose(t2 - t1, 1.5)
    # Test that a diff from the beginning of the leap second to the beginning of the next
    # day is no longer than a second
    t1 = DateTime('2015-06-30 23:59:60.').secs
    t2 = DateTime('2015-07-01 00:00:00').secs
    np.isclose(t2 - t1, 1.0)


def test_leapsec_2016():
    """
    Tests for end of 2016 leap second. (PR #23).
    """
    # Test that there are 4 clock ticks where one usually expects 3
    t1 = DateTime('2016-12-31 23:59:59').secs
    t2 = DateTime('2017-01-01 00:00:02').secs
    np.isclose(t2 - t1, 4.0)
    # Test that a diff from a time before to the middle of the leap second is consistent
    t1 = DateTime('2016-12-31 23:59:59').secs
    t2 = DateTime('2016-12-31 23:59:60.5').secs
    np.isclose(t2 - t1, 1.5)
    # Test that a diff from the beginning of the leap second to the beginning of the year
    # is no longer than a second
    t1 = DateTime('2016-12-31 23:59:60.').secs
    t2 = DateTime('2017-01-01 00:00:00').secs
    np.isclose(t2 - t1, 1.0)


def test_date_now():
    """
    Make sure that instantiating a DateTime object as NOW uses the
    the time at creation, not the time at attribute access.
    """
    date1 = DateTime()
    date1_date = date1.date
    time.sleep(1)
    assert date1.date == date1_date


def test_date_attributes():
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
        assert np.all(getattr(t, attr) == vals)

    t = DateTime('2015:160:02:24:00.250')
    for attr, val in (('year', 2015),
                      ('yday', 160),
                      ('hour', 2),
                      ('min', 24),
                      ('sec', 0.25),
                      ('mon', 6),
                      ('day', 9),
                      ('wday', 1)):
        assert getattr(t, attr) == val


def test_cxotime_now():
    """Check instantiating with CxoTime.NOW results in current time."""
    # These two commands should run within a 2 sec of each other, even on the slowest
    # machine.
    date1 = DateTime(CxoTime.NOW)
    date2 = DateTime()
    assert abs(date2.secs - date1.secs) < 2.0


def test_with_object_input():
    """Check DateTime fails when called with an object() that is not CxoTime.NOW"""
    with pytest.raises(ChandraTimeError):
        DateTime(object()).iso


def test_cxotime_now_env_var(monkeypatch):
    """Check instantiating with CxoTime.NOW results in current time."""
    # These two commands should run within a 2 sec of each other, even on the slowest
    # machine.
    date = '2015:160:02:24:01.250'
    monkeypatch.setenv('CXOTIME_NOW', date)
    assert DateTime(CxoTime.NOW).date == date
    assert DateTime().date == date
    assert DateTime(None).date == date

    # Ensure that env var does not disrupt normal operation
    assert DateTime('2025:001:00:00:01.250').date == '2025:001:00:00:01.250'
