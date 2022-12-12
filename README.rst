Convert between various time formats relevant to Chandra.

chandra_time provides a simple interface to the C++ time conversion
utility axTime3 (which itself is a wrapper for XTime) written by Arnold
Rots.  chandra_time also supports some useful additional time formats.

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

  >>> from chandra_time import DateTime
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

Input and output time system
----------------------------

Currently the object-oriented interface does not allow you to adjust the
input or output time system.  If you really need to do this, use the package
function convert()::

  >>> import chandra_time
  >>> chandra_time.convert(53614.0,
  ...                      fmt_in='mjd',
  ...                      sys_in='tt',
  ...                      fmt_out='caldate',
  ...                      sys_out='tai')
  '2005Aug31 at 23:59:27.816'

The convert() routine will guess fmt_in and supply a default for sys_in if not
specified.  As for DateTime() the input time can be a sequence or numpy array.
