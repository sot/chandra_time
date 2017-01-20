"""
Convert between various time formats relevant to Chandra.

Chandra.Time provides a simple interface to the C++ time conversion
utility axTime3 (which itself is a wrapper for XTime) written by Arnold
Rots.  Chandra.Time also supports some useful additional time formats.

The supported time formats are:

============ ==============================================  =======
 Format      Description                                     System
============ ==============================================  =======
  secs       Seconds since 1998-01-01T00:00:00 (float)       tt
  numday     DDDD:hh:mm:ss.ss... Elapsed days and time       utc
  relday     [+-]<float> Relative number of days from now    utc
  jd         Julian Day                                      utc
  mjd        Modified Julian Day = JD - 2400000.5            utc
  date       YYYY:DDD:hh:mm:ss.ss..                          utc
  caldate    YYYYMonDD at hh:mm:ss.ss..                      utc
  fits       YYYY-MM-DDThh:mm:ss.ss..                        tt
  iso        YYYY-MM-DD hh:mm:ss.ss..                        utc
  unix       Unix time (since 1970.0)                        utc
  greta      YYYYDDD.hhmmss[sss]                             utc
  year_doy   YYYY:DDD                                        utc
  mxDateTime mx.DateTime object                              utc
  frac_year  YYYY.ffffff = date as a floating point year     utc
  plotdate   Matplotlib plotdate (days since year 0)         utc
============ ==============================================  =======

Each of these formats has an associated time system, which must be one of:

=======  ============================
  met     Mission Elapsed Time 
  tt      Terrestrial Time 
  tai     International Atomic Time 
  utc     Coordinated Universal Time 
=======  ============================


Usage
-----

The normal usage is to create an object that allows conversion from one time
format to another.  Conversion takes place by examining the appropriate
attribute.  Unless the time format is specified or it is ambiguous (i.e. secs,
jd, mjd, and unix), the time format is automatically determined.  To
specifically select a format use the 'format' option.::

  >>> from Chandra.Time import DateTime
  >>> t = DateTime('1999-07-23T23:56:00')
  >>> print t.date
  1999:204:23:54:55.816
  >>> t.date
  '1999:204:23:54:55.816'
  >>> t.secs
  49161360.0
  >>> t.jd
  2451383.496479352
  >>> DateTime(t.jd + 1, format='jd').fits
  '1999-07-24T23:56:00.056'
  >>> DateTime(t.mjd + 1, format='mjd').caldate
  '1999Jul24 at 23:54:55.820'
  >>> u = DateTime(1125538824.0, format='unix')
  >>> u.date
  '2005:244:01:40:24.000'
  >>> mxd = mx.DateTime.Parser.DateTimeFromString('1999-01-01 12:13:14')
  >>> DateTime(mxd).fits
  '1999-01-01T12:14:18.184'
  >>> DateTime(mxd).date
  '1999:001:12:13:14.000'
  >>> DateTime(mxd).mxDateTime.strftime('%c')
  'Fri Jan  1 12:13:14 1999'
  >>> DateTime('2007122.01020340').date
  '2007:122:01:02:03.400'

If no input time is supplied when creating the object then the current time is used.::

  >>> DateTime().fits
  '2009-11-14T18:24:14.504'

For convenience a DateTime object can be initialized from another DateTime object.

  >>> t = DateTime()
  >>> u = DateTime(t)


Sequences of dates
------------------

The input time can also be an iterable sequence (returns a list) or
a numpy array (returns a numpy array with the same shape)::

  >>> import numpy
  >>> DateTime([1,'2001:255',3]).date
  ['1997:365:23:58:57.816', '2001:255:12:00:00.000', '1997:365:23:58:59.816']
  >>> DateTime(numpy.array([[1,2],[3,4]])).fits
  array([['1998-01-01T00:00:01.000', '1998-01-01T00:00:02.000'],
         ['1998-01-01T00:00:03.000', '1998-01-01T00:00:04.000']], 
        dtype='|S23')


Date arithmetic
---------------

DateTime objects support a limited arithmetic with a delta time expressed in days.
One can add a delta time to a DateTime or subtract a delta time from a DateTime.
It is also possible to subtract two DateTiem objects to get a delta time in days.
If the DateTime holds a NumPy array or the delta times are NumPy arrays then the
appropriate broadcasting will be done.
::

  >>> d1 = DateTime('2011:200:00:00:00')
  >>> d2 = d1 + 4.25
  >>> d2.date
  '2011:204:06:00:00.000'
  >>> d2 - d1
  4.25
  >>> import numpy as np
  >>> d3 = d1 + np.array([1,2,3])
  >>> d3.date
  array(['2011:201:00:00:00.000', '2011:202:00:00:00.000',
         '2011:203:00:00:00.000'], 
        dtype='|S21')
  >>> (d3 + 7).year_doy
  array(['2011:208', '2011:209', '2011:210'], 
        dtype='|S8')


Fast conversion functions
-------------------------

The DateTime class does full validation and format-detection of input
values.  In cases where this is not necessary a substantial improvement in
speed (factor of 4 to 12) can be obtained using functions that skip the
validation and format detection.  See the documentation for
:func:`~Chandra.Time.date2secs`, :func:`~Chandra.Time.secs2date`, and
:func:`~Chandra.Time.convert_vals`.
::

  >>> from Chandra.Time import date2secs, secs2date, convert_vals
  >>> date2secs('2001:001:01:01:01')
  94698125.18399999
  >>> dates = secs2date([0, 1e8, 2e8])
  >>> dates
  array(['1997:365:23:58:56.816', '2001:062:09:45:35.816', '2004:124:19:32:15.816'],
        dtype='|S21')
  >>> date2secs(dates)
  array([  0.00000000e+00,   1.00000000e+08,   2.00000000e+08])
  >>> convert_vals(dates, 'date', 'mjd')
  array([ 50813.9992687 ,  51971.40666454,  53128.81407194])
  >>> convert_vals(dates, 'date', 'secs')
  array([  0.00000000e+00,   1.00000000e+08,   2.00000000e+08])


Input and output time system
----------------------------

Currently the object-oriented interface does not allow you to adjust the
input or output time system.  If you really need to do this, use the package
function convert()::

  >>> import Chandra.Time
  >>> Chandra.Time.convert(53614.0,
  ...                      fmt_in='mjd',
  ...                      sys_in='tt',
  ...                      fmt_out='caldate',
  ...                      sys_out='tai')
  '2005Aug31 at 23:59:27.816'

The convert() routine will guess fmt_in and supply a default for sys_in if not
specified.  As for DateTime() the input time can be a sequence or numpy array.

Time attributes
---------------

A ``DateTime`` object has additional attributes ``year``, ``mon``, ``day``,
``hour``, ``min``, ``sec``, ``yday``, and ``wday``.  These provide the
year, month (1-12), day of month (1-31), hour (0-23), minute (0-59), second (0-60),
day of year (1-366), and day of week (0-6, where 0 is Monday).

These are all referenced to UTC time.
"""
import sys
import re
from functools import wraps
import warnings
import time

import six
import numpy as np


def override__dir__(f):
    """
    When overriding a __dir__ method on an object, you often want to
    include the "standard" members on the object as well.  This
    decorator takes care of that automatically, and all the wrapped
    function needs to do is return a list of the "special" members
    that wouldn't be found by the normal Python means.

    Example
    -------

    @override__dir__
    def __dir__(self):
        return ['special_method1', 'special_method2']

    This method is copied from astropy.utils.compat.misc, with a slight change to
    remove the six dependency.
    """
    if sys.version_info[:2] < (3, 3):
        # There was no straightforward way to do this until Python 3.3, so
        # we have this complex monstrosity
        @wraps(f)
        def override__dir__wrapper(self):
            members = set()
            for cls in self.__class__.mro():
                members.update(dir(cls))
            members.update(self.__dict__)
            members.update(f(self))
            return sorted(members)
    else:
        # http://bugs.python.org/issue12166

        @wraps(f)
        def override__dir__wrapper(self):
            members = set(object.__dir__(self))
            members.update(f(self))
            return sorted(members)

    return override__dir__wrapper


class TimeAttribute(object):
    def __init__(self, attr):
        self.attr = attr

    def __get__(self, instance, owner):
        return instance.time_attributes[self.attr]


class TimeStyle(object):
    def __init__(self,
                 name,
                 ax3_fmt,
                 ax3_sys,
                 match_expr = None,
                 match_func = lambda x,y: re.match(x,y).group(),
                 match_err  = AttributeError,
                 postprocess= None,
                 preprocess= None,
                 dtype=None,
                 ):
        self.name = name
        self.match_expr = match_expr
        self.match_func = match_func
        self.match_err  = match_err
        self.ax3_fmt = ax3_fmt
        self.ax3_sys = ax3_sys
        self.postprocess = postprocess
        self.preprocess = preprocess
        self.dtype = dtype
        
    def match(self, time):
        try:
            self.time_in = self.match_func(self.match_expr, time)
            return True
        except self.match_err:
            pass
        return False

T1998 = 883612736.816  # Seconds from 1970:001:00:00:00 (UTC) to 1998-01-01T00:00:00 (TT)
RE = {'float'       : r'[+-]?(?:\d+[.]?\d*|[.]\d+)(?:[dDeE][+-]?\d+)?$',
      'date'        : r'^(\d{4}):(\d{3}):(\d{2}):(\d{2}):(\d{2})(\.\d*)?$',
      'year_doy'    : r'^(\d{4}):(\d{3})$',
      'caldate'     : r'^\d{4}\w{3}\d{1,2}\s+at\s+\d{1,2}:\d{1,2}:\d{1,2}(\.\d*)?$',
      'greta'       : r'^(\d{4})(\d{3})\.(\d{2})?(\d{2})?(\d{2})?(\d+)?$',
      'fits'        : r'^\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}(\.\d*)?$',
      'year_mon_day': r'^\d{4}-\d{1,2}-\d{1,2}$',
      'iso'         : r'^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}(\.\d*)?$',
      }

# Conversions for greta format
def greta_to_date(date_in):
    # Force date_in string to have 9 digits of precision to represent
    # hhmmssfff (where fff is milliseconds within the second)
    date_in = '{:.9f}'.format(float(date_in))
    m = re.match(RE['greta'], date_in)
    out = '%s:%s:%s:%s:%s' % m.groups()[0:5]
    if m.group(6) != None:
        out += '.%s' % m.group(6)
    return out

def date_to_greta(date_in):
    m = re.match(RE['date'], date_in)
    out = '%s%s.%s%s%s' % m.groups()[0:5]
    if m.group(6) != None:
        frac = m.group(6).replace('.', '')
        out += frac
    return out

# Conversions for frac_year format
_year_secs = {}                 # Start and end secs for a year
def year_start_end_secs(year):
    return (DateTime('%04d:001:00:00:00' % year).secs,
            DateTime('%04d:001:00:00:00' % (year + 1)).secs)

def frac_year_to_secs(frac_year):
    frac_year = float(frac_year)
    year = int(frac_year)
    s0, s1 = _year_secs.setdefault(year, year_start_end_secs(year))
    return repr((frac_year - year) * (s1 - s0) + s0)

def secs_to_frac_year(secs):
    year = int(DateTime(secs).date[:4])
    s0, s1 = _year_secs.setdefault(year, year_start_end_secs(year))
    return (float(secs) - s0) / (s1 - s0) + year

def raise_(r):
    raise r

def mx_DateTime_ISO_ParseDateTime(t):
    try:
        import mx.DateTime
        warnings.warn('mxDateTime format will be removed soon, ask TLA for migration options')
        return mx.DateTime.ISO.ParseDateTime(t)
    except ImportError:
        raise ValueError('mxDateTime format is unavailable, ask TLA for migration options')


time_styles = [ TimeStyle(name       = 'fits',
                          match_expr = RE['fits'],
                          ax3_fmt    = 'f3',
                          ax3_sys    = 't',
                          dtype      = 'S23',
                          ),
                TimeStyle(name       = 'year_mon_day',
                          match_expr = RE['year_mon_day'],
                          ax3_fmt    = 'f3',
                          ax3_sys    = 'u',
                          preprocess = lambda t: t + 'T12:00:00',
                          postprocess= lambda t: re.sub(r'T\d{2}:\d{2}:\d{2}\.\d+$', '', t),
                          ),
                TimeStyle(name       = 'relday',
                          match_expr = r'^[+-]' + RE['float'] + '$',  # DDDD:hh:mm:ss.ss.
                          ax3_fmt    = 's',
                          ax3_sys    = 'u',
                          preprocess = lambda x: str(time.time() + float(x)*86400.0 - T1998),
                          postprocess= lambda x: (float(x) + T1998 - time.time()) / 86400.0,
                          ),
                TimeStyle(name       = 'greta',
                          match_expr = RE['greta'],
                          match_func = lambda f,t: ((float(t) < 2099001.000000 or raise_(ValueError))
                                                    and re.match(f,t).group()),
                          match_err  = (AttributeError, ValueError),
                          ax3_fmt    = 'd3',
                          ax3_sys    = 'u',
                          preprocess = greta_to_date,
                          postprocess= date_to_greta,
                          ),
                TimeStyle(name       = 'secs',
                          match_expr = '^' + RE['float'] + '$',
                          ax3_fmt    = 's',
                          ax3_sys    = 'm',
                          postprocess= float,
                          dtype      = np.float64,
                          ),
                TimeStyle(name       = 'frac_year',
                          match_expr = '^' + RE['float'] + '$',
                          ax3_fmt    = 's',
                          ax3_sys    = 'm',
                          preprocess = frac_year_to_secs,
                          postprocess= secs_to_frac_year,
                          ),
                TimeStyle(name       = 'unix',
                          match_expr = '^' + RE['float'] + '$',
                          ax3_fmt    = 's',
                          ax3_sys    = 'u',
                          preprocess = lambda x: repr(float(x) - T1998),
                          postprocess= lambda x: float(x) + T1998,
                          ),
                TimeStyle(name       = 'iso',
                          match_expr = RE['iso'],
                          ax3_fmt    = 'f3', 
                          ax3_sys    = 'u',
                          preprocess = lambda t: t.replace(' ', 'T'),
                          postprocess= lambda t: t.replace('T', ' '),
                          ),
                TimeStyle(name       = 'mxDateTime',
                          match_expr = RE['iso'],
                          ax3_fmt    = 'f3', 
                          ax3_sys    = 'u',
                          preprocess = lambda t: t.replace(' ', 'T'),
                          postprocess= mx_DateTime_ISO_ParseDateTime,
                          ),
                TimeStyle(name       = 'caldate',
                          match_expr = RE['caldate'],
                          ax3_fmt    = 'c3',
                          ax3_sys    = 'u',
                          dtype      = 'S25',
                          ),
                TimeStyle(name       = 'date',
                          match_expr = RE['date'],
                          ax3_fmt    = 'd3',
                          ax3_sys    = 'u',
                          dtype      = 'S21',
                          ),
                TimeStyle(name       = 'year_doy',
                          match_expr = RE['year_doy'],
                          ax3_fmt    = 'd3',
                          ax3_sys    = 'u',
                          preprocess = lambda t: t + ':12:00:00',
                          postprocess= lambda t: re.sub(r':\d{2}:\d{2}:\d{2}\.\d+$', '', t),
                          ),
                TimeStyle(name       = 'jd',
                          match_expr = '^' + RE['float'] + '$',
                          ax3_fmt    = 'j',
                          ax3_sys    = 'u',
                          postprocess= float,
                          dtype      = np.float64,
                          ),
                TimeStyle(name       = 'mjd',
                          match_expr = '^' + RE['float'] + '$',
                          ax3_fmt    = 'm',
                          ax3_sys    = 'u',
                          postprocess= float,
                          dtype      = np.float64,
                          ),
                TimeStyle(name       = 'numday',
                          match_expr = r'^\d{1,4}:\d{1,2}:\d{1,2}:\d{1,2}(\.\d*)?$',  # DDDD:hh:mm:ss.ss.
                          ax3_fmt    = 'n3',
                          ax3_sys    = 'u',
                          ),
                TimeStyle(name       = 'plotdate',
                          match_expr = '^' + RE['float'] + '$',
                          ax3_fmt    = 'j',
                          ax3_sys    = 'u',
                          preprocess = lambda x: repr(float(x) + 1721424.5),
                          postprocess= lambda x: float(x) - 1721424.5,
                          ),
                ]

time_system = {'met' : 'm',  #  MET     Mission Elapsed Time ("m")		  
               'tt'  : 't',  #  TT      Terrestrial Time ("t")		  
               'tai' : 'a',  #  TAI     International Atomic Time ("ta" or "a")
               'utc' : 'u',  #  UTC     Coordinated Universal Time ("u")       
               }
 
# Preloaded methods go here.

class ChandraTimeError(ValueError):
    """Exception class for bad input values to Chandra.Time"""


def _make_array(val):
    """
    Take ``val`` and convert/reshape to a 1-d array.  If ``copy`` is True
    then copy input values.

    Returns
    -------
    val, val_ndim: ndarray, int
        Array version of ``val`` and the number of dims in original.
    """
    val = np.array(val)
    val_ndim = val.ndim  # remember original ndim
    if val.ndim == 0:
        val = np.asarray([val])

    # Allow only string or float arrays as input (XXX datetime later...)
    if val.dtype.kind == 'i':
        val = np.asarray(val, dtype=np.float64)

    return val, val_ndim


def convert_vals(vals, format_in, format_out):
    """
    Convert ``vals`` from the input ``format_in`` to the output format
    ``format_out``.  This does **no input validation** and thus runs much faster
    than the corresponding DateTime() conversion.  Be careful because invalid
    inputs can give unpredictable results.

    The input ``vals`` can be a single (scalar) value, a Python list or a numpy
    array.  The output data type is specified with ``dtype`` which must be a
    valid numpy dtype.

    The input and output format should be one of the following DateTime
    format names: 'secs', 'date', 'jd', 'mjd', 'fits', 'caldate'.

    The function returns the converted time as either a scalar or a numpy
    array, depending on the input ``vals``.

    :param vals: input values (scalar, list, array)
    :param fmt_in: input format (e.g. 'secs', 'date', 'jd', ..)
    :param fmt_out: output format (e.g. 'secs', 'date', 'jd', ..)

    :returns: converted values as either scalar or numpy array
    """
    from . import _axTime3 as axTime3

    def get_style(fmt):
        # Only the styles with a dtype attribute can be converted using this function.
        ok_styles = [x for x in time_styles if x.dtype]
        for time_style in ok_styles:
            if time_style.name == fmt:
                return time_style.ax3_sys, time_style.ax3_fmt, time_style.dtype
        else:
            raise ValueError('Error - specified format {} is not an allowed value {}'
                             .format(fmt, [x.name for x in ok_styles]))

    sys_in, fmt_in, dtype_in = get_style(format_in)
    sys_out, fmt_out, dtype_out = get_style(format_out)

    vals, ndim = _make_array(vals)
    # If the input is already string-like then pass straight to convert_time.
    # Otherwise convert to string with repr().
    if vals.dtype.char in 'SU':
        outs = [axTime3.convert_time(val, sys_in, fmt_in, sys_out, fmt_out)
                for val in vals.flatten()]
    else:
        outs = [axTime3.convert_time(repr(val), sys_in, fmt_in, sys_out, fmt_out)
                for val in vals.flatten()]

    if (six.PY3
            and isinstance(dtype_out, six.string_types)
            and dtype_out.startswith('S')):
        dtype_out = 'U' + dtype_out[1:]
    outs = np.array(outs, dtype=dtype_out)
    
    return (outs[0].tolist() if ndim == 0 else outs.reshape(vals.shape))


def date2secs(dates):
    """
    Convert ``dates`` from the ``date`` system (e.g. '2011:001:12:23:45.001') to
    the ``secs`` system (CXC seconds).  This does **no input validation** and
    thus runs much faster than the corresponding ``DateTime(dates).secs``
    conversion.  Be careful because invalid inputs can give unpredictable
    results.

    The input ``dates`` can be a single (scalar) value, a Python list or a numpy
    array.  The shape of the output matches the shape of the input.

    :param dates: input dates (scalar, list, array of strings)
    :returns: converted times as either scalar or numpy array (float)
    """
    return convert_vals(dates, 'date', 'secs')

def secs2date(times):
    """
    Convert ``times`` from the ``secs`` system (CXC seconds) to the ``date``
    system (e.g. '2011:001:12:23:45.001').  This does **no input validation**
    and thus runs much faster than the corresponding ``DateTime(times).date``
    conversion.  Be careful because invalid inputs can give unpredictable
    results.

    The input ``times`` can be a single (scalar) value, a Python list or a numpy
    array.  The shape of the output matches the shape of the input.

    :param times: input times (scalar, list, array of floats)
    :returns: converted dates as either scalar or numpy array (string)
    """
    return convert_vals(times, 'secs', 'date')


def convert(time_in, sys_in=None, fmt_in=None, sys_out=None, fmt_out='secs'):
    """Base routine to convert from/to any format."""
    if time_in is None:
        time_in = time.time()
        fmt_in = 'unix'
        sys_in = None

    # Does is behave like a numpy ndarray with non-zero dimension?
    if hasattr(time_in, 'shape') and hasattr(time_in, 'flatten') and time_in.shape:
        import numpy
        time_out = [_convert(x, sys_in, fmt_in, sys_out, fmt_out) for x in time_in.flatten()]
        return numpy.array(time_out).reshape(time_in.shape)
    else:
        # If time_in is not string-like then try iterating over it
        try:
            if str(time_in) == time_in:
                raise TypeError
            return [_convert(x, sys_in, fmt_in, sys_out, fmt_out) for x in time_in]
        except TypeError:
            return _convert(time_in, sys_in, fmt_in, sys_out, fmt_out)

def _convert(time_in, sys_in, fmt_in, sys_out, fmt_out):
    """Base routine to convert from/to any format."""

    from . import _axTime3 as axTime3

    # See if time_in works as a float after first getting the string version.
    # For an actual float input this then gets the full-precision representation.
    # For time_in = mx.DateTime object then the try will fail through.
    try:
        float(str(time_in))
        time_in = repr(float(time_in))
    except ValueError:
        time_in = str(time_in)

    for time_style in time_styles:
        if fmt_in and time_style.name != fmt_in:
            continue 
        if time_style.match(time_in):
            time_in = time_style.time_in
            ax3_fmt_in = time_style.ax3_fmt
            ax3_sys_in = time_style.ax3_sys
            preprocess = time_style.preprocess
            break
    else:
        raise ChandraTimeError("Invalid input format '%s'" % fmt_in)

    if sys_in:
        if sys_in in time_system:
            ax3_sys_in = time_system[sys_in]
        else:
            raise ChandraTimeError("Invalid input system '%s'" % sys_in)
        
    for time_style in time_styles:
        if time_style.name == fmt_out:
            ax3_fmt_out = time_style.ax3_fmt
            ax3_sys_out = time_style.ax3_sys
            postprocess = time_style.postprocess
            break
    else:
        raise ChandraTimeError("Invalid output format '%s'" % fmt_out)

    if sys_out:
        if sys_out in time_system:
            ax3_sys_out = time_system[sys_out]
        else:
            raise ChandraTimeError("Invalid output system '%s'" % sys_out)

    if preprocess:
        time_in = preprocess(time_in)
        
    time_out = axTime3.convert_time(time_in,
                                    ax3_sys_in,
                                    ax3_fmt_in,
                                    ax3_sys_out,
                                    ax3_fmt_out,
                                    )

    if postprocess: time_out = postprocess(time_out)

    return time_out

class DateTime(object):
    """
    DateTime - Convert between various time formats

    The supported time formats are:

    ============ ==============================================  =======
     Format      Description                                     System
    ============ ==============================================  =======
      secs       Seconds since 1998-01-01T00:00:00 (float)       tt
      numday     DDDD:hh:mm:ss.ss... Elapsed days and time       utc
      relday     [+-]<float> Relative number of days from now    utc
      jd         Julian Day                                      utc
      mjd        Modified Julian Day = JD - 2400000.5            utc
      date       YYYY:DDD:hh:mm:ss.ss..                          utc
      caldate    YYYYMonDD at hh:mm:ss.ss..                      utc
      fits       YYYY-MM-DDThh:mm:ss.ss..                        tt
      iso        YYYY-MM-DD hh:mm:ss.ss..                        utc
      unix       Unix time (since 1970.0)                        utc
      greta      YYYYDDD.hhmmss[sss]                             utc
      year_doy   YYYY:DDD                                        utc
      mxDateTime mx.DateTime object                              utc
      frac_year  YYYY.ffffff = date as a floating point year     utc
      plotdate   Matplotlib plotdate (days since 0001-01-01)     utc
    ============ ==============================================  =======

    Each of these formats has an associated time system, which must be one of:

    =======  ============================
      met     Mission Elapsed Time
      tt      Terrestrial Time
      tai     International Atomic Time
      utc     Coordinated Universal Time
    =======  ============================

    :param time_in: input time (current time if not supplied)
    :param format: format of input time ()

    :returns: DateTime object
    """
    def __init__(self, time_in=None, format=None):
        # If no time_in supplied this implies NOW.
        if time_in is None:
            if format is not None:
                raise ValueError('Cannot supply `format` without `time_in`')
            time_in = time.time()
            format = 'unix'

        try:
            self.time_in = time_in.time_in
            self.format = time_in.format
        except AttributeError:
            self.time_in = time_in
            self.format  = format

    def __getattr__(self, fmt_out):
        if fmt_out.startswith('_'):
            return self.__getattribute__(fmt_out)

        return convert(self.time_in,
                       fmt_in=self.format,
                       fmt_out=fmt_out,
                       )

    def __add__(self, days):
        return DateTime(self.jd + days, format='jd')

    def __sub__(self, other):
        if isinstance(other, DateTime):
            return self.jd - other.jd
        else:
            return DateTime(self.jd - other, format='jd')

    @override__dir__
    def __dir__(self):
        return [time_style.name for time_style in time_styles]

    def day_start(self):
        """Return a new DateTime object corresponding to the start of the day."""
        date = self.date.split(':')
        return DateTime('%s:%s:00:00:00' % (date[0], date[1]))

    def day_end(self):
        """Return a new DateTime object corresponding to the end of the day."""
        date = self.date.split(':')
        return DateTime('%s:%03d:00:00:00' % (date[0], int(date[1])+1))

    @property
    def time_attributes(self):
        if hasattr(self, '_time_attributes'):
            return self._time_attributes

        if not hasattr(self, '_time_attributes'):
            # date       YYYY:DDD:hh:mm:ss.ss..                          utc
            # iso        YYYY-MM-DD hh:mm:ss.ss..                        utc
            date = self.date
            iso = self.iso
            mjd = self.mjd

            # Coerce list output into np.array
            if isinstance(date, list):
                date = np.array(date)
                iso = np.array(iso)
                mjd = np.array(mjd)

            monday_mjd = DateTime('2015:159:00:00:00').mjd
            is_array = hasattr(date, 'shape') and hasattr(date, 'flatten') and date.shape

            def slice_string(val, i0, i1, out_type):
                slc = slice(i0, i1)
                if is_array:
                    out = np.array([x[slc] for x in val]).astype(out_type)
                else:
                    out = out_type(val[slc])
                return out

            ta = {}
            ta['year'] = slice_string(date, 0, 4, int)
            ta['yday'] = slice_string(date, 5, 8, int)
            ta['hour'] = slice_string(date, 9, 11, int)
            ta['min'] = slice_string(date, 12, 14, int)
            ta['sec'] = slice_string(date, 15, None, float)
            ta['mon'] = slice_string(iso, 5, 7, int)
            ta['day'] = slice_string(iso, 8, 10, int)
            wday = np.mod(np.floor(mjd - monday_mjd), 7)
            ta['wday'] = wday.astype(int) if is_array else int(wday)

            self._time_attributes = ta

        return self._time_attributes

    year = TimeAttribute('year')
    yday = TimeAttribute('yday')
    hour = TimeAttribute('hour')
    min = TimeAttribute('min')
    sec = TimeAttribute('sec')
    mon = TimeAttribute('mon')
    day = TimeAttribute('day')
    wday = TimeAttribute('wday')


def command_line_convert_time():
    import argparse

    parser = argparse.ArgumentParser(description='Convert time to standard formats',
                                     usage='convert_time [-h] [time] [format]')

    parser.add_argument('time',
                        type=str,
                        nargs='?',
                        default=None,
                        help='Input time in any Chandra.Time format')

    parser.add_argument('format',
                        type=str,
                        nargs='?',
                        default=None,
                        help='Input format')
    args = parser.parse_args()

    time_in = args.time
    format = args.format

    print(DateTime(time_in, format).fits)
    print(DateTime(time_in, format).caldate)
    print(DateTime(time_in, format).date)
    print(DateTime(time_in, format).secs)
    print(DateTime(time_in, format).jd)

if __name__ == '__main__':
    command_line_convert_time()
