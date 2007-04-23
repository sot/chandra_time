"""Convert between various time formats relevant to Chandra.

Chandra::Time provides a simple interface to the C++ time conversion
utility axTime3 (which itself is a wrapper for XTime) written by Arnold
Rots.  

The supported time formats are:

 Format   Description                                     System
-------   ------------------------------------------      -------
  secs    Elapsed seconds since 1998-01-01T00:00:00       tt
  numday  DDDD:hh:mm:ss.ss... Elapsed days and time       utc
  jd      Julian Day                                      utc
  mjd     Modified Julian Day = JD - 2400000.5            utc
  date    YYYY:DDD:hh:mm:ss.ss..                          utc
  caldate YYYYMonDD at hh:mm:ss.ss..                      utc
  fits    FITS date/time format YYYY-MM-DDThh:mm:ss.ss..  tt
  unix    Unix time (since 1970.0)                        utc

Each of these formats has an associated time system, which are be one of:

  met     Mission Elapsed Time 
  tt      Terrestrial Time 
  tai     International Atomic Time 
  utc     Coordinated Universal Time 

The normal usage is to create an object that allows conversion from one time
format to another.  Conversion takes place by examining the appropriate
attribute.  Unless the time format is specified or it is ambiguous (i.e. secs,
jd, mjd, and unix), the time format is automatically determined.  To
specifically select a format use the 'format' option.

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

Currently the object-oriented interface does not allow you to adjust the
input or output time system.  If you really need to do this, use the package
function convert():

>>> import Chandra.Time
>>> Chandra.Time.convert(53614.0,
...                      fmt_in='mjd',
...                      sys_in='tt',
...                      fmt_out='caldate',
...                      sys_out='tai')
'2005Aug31 at 23:59:27.816'

The convert() routine will guess fmt_in and supply a default for sys_in if not
specified.
"""

import re
import axTime3

# Import mx.DateTime if possible
try: import mx.DateTime
except ImportError: pass

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
                 ):
        self.name = name
        self.match_expr = match_expr
        self.match_func = match_func
        self.match_err  = match_err
        self.ax3_fmt = ax3_fmt
        self.ax3_sys = ax3_sys
        self.postprocess = postprocess
        self.preprocess = preprocess
        
    def match(self, time):
        try:
            self.time_in = self.match_func(self.match_expr, time)
            return True
        except self.match_err:
            pass
        return False

T1998 = 883612736.816  # Seconds from 1970:001:00:00:00 (UTC) to 1998-01-01T00:00:00 (TT)
RE = {'float'   : r'[+-]?(?:\d+[.]?\d*|[.]\d+)(?:[dDeE][+-]?\d+)?',
      'date'    : r'^(\d{4}):(\d{3}):(\d{2}):(\d{2}):(\d{2})(\.\d*)?',
      'caldate' : r'^\d{4}\w{3}\d{1,2}\s+at\s+\d{1,2}:\d{1,2}:\d{1,2}(\.\d*)?$',
      'greta'   : r'^(\d{4})(\d{3})\.(\d{2})(\d{2})(\d{2})(\d+)?$',
      'fits'    : r'^\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}(\.\d*)?$',
      }

def greta_to_date(date_in):
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

time_styles = [ TimeStyle(name       = 'fits',
                          match_expr = RE['fits'],
                          ax3_fmt    = 'f3',
                          ax3_sys    = 't',
                          ),
                TimeStyle(name       = 'greta',
                          match_expr = RE['greta'],
                          match_func = lambda f,t: float(t) < 2099001.000000 and re.match(f,t).group(),
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
                          postprocess= float ,
                          ),
                TimeStyle(name       = 'unix',
                          match_expr = '^' + RE['float'] + '$',
                          ax3_fmt    = 's',
                          ax3_sys    = 'u',
                          preprocess = lambda x: str(float(x) - T1998),
                          postprocess= lambda x: float(x) + T1998,
                          ),
                TimeStyle(name       = 'iso',
                          match_func = lambda f,t: mx.DateTime.ISO.ParseDateTime(t),
                          match_err  = ValueError,
                          ax3_fmt    = 'f3', 
                          ax3_sys    = 'u',
                          preprocess = lambda t: t.date + 'T' + t.time,
                          postprocess= lambda t: t.replace('T', ' '),
                          ),
                TimeStyle(name       = 'mxDateTime',
                          match_func = lambda f,t: mx.DateTime.ISO.ParseDateTime(t),
                          match_err  = ValueError,
                          ax3_fmt    = 'f3', 
                          ax3_sys    = 'u',
                          preprocess = lambda t: t.date + 'T' + t.time,
                          postprocess= lambda t: mx.DateTime.ISO.ParseDateTime(t),
                          ),
                TimeStyle(name       = 'caldate',
                          match_expr = RE['caldate'],
                          ax3_fmt    = 'c3',
                          ax3_sys    = 'u',
                          ),
                TimeStyle(name       = 'date',
                          match_expr = RE['date'],
                          ax3_fmt    = 'd3',
                          ax3_sys    = 'u',
                          ),
                TimeStyle(name       = 'jd',
                          match_expr = '^' + RE['float'] + '$',
                          ax3_fmt    = 'j',
                          ax3_sys    = 'u',
                          postprocess= float,
                          ),
                TimeStyle(name       = 'mjd',
                          match_expr = '^' + RE['float'] + '$',
                          ax3_fmt    = 'm',
                          ax3_sys    = 'u',
                          postprocess= float,
                          ),
                TimeStyle(name       = 'numday',
                          match_expr = r'^\d{1,4}:\d{1,2}:\d{1,2}:\d{1,2}(\.\d*)?$',  # DDDD:hh:mm:ss.ss.
                          ax3_fmt    = 'n3',
                          ax3_sys    = 'u',
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

def convert(time_in, sys_in=None, fmt_in=None, sys_out=None, fmt_out='secs'):
    """Base routine to convert from/to any format."""

    time_in = str(time_in)
    for time_style in time_styles:
        if fmt_in and time_style.name != fmt_in: continue 
        if time_style.match(time_in):
            time_in = time_style.time_in
            ax3_fmt_in = time_style.ax3_fmt
            ax3_sys_in = time_style.ax3_sys
            preprocess = time_style.preprocess
            break
    else:
        raise ChandraTimeError, "Invalid input format '%s'" % fmt_in

    if sys_in:
        if sys_in in time_system:
            ax3_sys_in = time_system[sys_in]
        else:
            raise ChandraTimeError, "Invalid input system '%s'" % sys_in
        
    for time_style in time_styles:
        if time_style.name == fmt_out:
            ax3_fmt_out = time_style.ax3_fmt
            ax3_sys_out = time_style.ax3_sys
            postprocess = time_style.postprocess
            break
    else:
        raise ChandraTimeError, "Invalid output format '%s'" % fmt_out

    if sys_out:
        if sys_out in time_system:
            ax3_sys_out = time_system[sys_out]
        else:
            raise ChandraTimeError, "Invalid output system '%s'" % sys_out

    if preprocess: time_in = preprocess(time_in)
        
    time_out = axTime3.convert_time(time_in,
                                    ax3_sys_in,
                                    ax3_fmt_in,
                                    ax3_sys_out,
                                    ax3_fmt_out,
                                    )

    if postprocess: time_out = postprocess(time_out)

    return time_out

class DateTime(object):
    """DateTime - Convert between various time formats

    """
    def __init__(self, time_in, format=None):
        self.time_in = time_in
        self.format  = format

    def __getattr__(self, fmt_out):
        return convert(self.time_in,
                       fmt_in=self.format,
                       fmt_out=fmt_out,
                       )
