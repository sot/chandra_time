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

T1998 = 883612736.816  # Seconds from 1970:001:00:00:00 (UTC) to 1998-01-01T00:00:00 (TT)
FloatRE = r'[+-]?(?:\d+[.]?\d*|[.]\d+)(?:[dDeE][+-]?\d+)?'
time_style = {'fits' : { 'match' : r'^\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}(\.\d*)?$',
                         'ax3_fmt' : 'f3',
                         'ax3_sys' : 't',
                         },
		 'caldate' : {'match' : r'^\d{4}\w{3}\d{1,2}\s+at\s+\d{1,2}:\d{1,2}:\d{1,2}(\.\d*)?$',
			       'ax3_fmt' : 'c3',
			       'ax3_sys' : 'u'
			      },
		 'date' : { 'match' : r'^\d{4}:\d{1,3}:\d{1,2}:\d{1,2}:\d{1,2}(\.\d*)?',
			     'ax3_fmt' : 'd3',
			     'ax3_sys' : 'u',
			   },
		 'secs' : { 'match' : r'^' + FloatRE + '$',
			    'ax3_fmt' : 's',
			    'ax3_sys' : 'm',
                            'typecast' : float,
			   },
		 'unix' : { 'match' : r'^' + FloatRE + '$',
			    'ax3_fmt' : 's',
			    'ax3_sys' : 'u',
                            'typecast' : float,
			   },
		 'jd'   : { 'match' : r'^' + FloatRE + '$',
                            'ax3_fmt' : 'j',
                            'ax3_sys' : 'u',
                            'typecast' : float,
			   },
		 'mjd'   : { 'match' : r'^' + FloatRE + '$',
                             'ax3_fmt' : 'm',
                             'ax3_sys' : 'u',
                             'typecast' : float,
			   },
		 'numday' : { 'match' : r'^\d{1,4}:\d{1,2}:\d{1,2}:\d{1,2}(\.\d*)?$',  # DDDD:hh:mm:ss.ss.
			     'ax3_fmt' : 'n3',
			     'ax3_sys' : 'u',
                              },
		}

_keys_time_style = ['fits', 'caldate', 'date', 'secs',
                   'unix', 'jd', 'mjd', 'numday'] # correct priority order

time_system = {'met' : 'm',  #  MET     Mission Elapsed Time ("m")		  
               'tt'  : 't',  #  TT      Terrestrial Time ("t")		  
               'tai' : 'a',  #  TAI     International Atomic Time ("ta" or "a")
               'utc' : 'u',  #  UTC     Coordinated Universal Time ("u")       
               }
 
# Preloaded methods go here.

class ChandraTimeError(ValueError):
    """Exception class for bad input values to Chandra.Time"""

def convert(time_in, sys_in=None, fmt_in=None, sys_out=None, fmt_out=None):
    """Base routine to convert from/to any format."""

    time_in = str(time_in)
    if fmt_in:
        if fmt_in in time_style:
            ax3_fmt_in = time_style[fmt_in]['ax3_fmt']
            ax3_sys_in = time_style[fmt_in]['ax3_sys']
            if not re.match(time_style[fmt_in]['match'], time_in):
                raise ChandraTimeError, \
                      'Time %s does not match expected format for %s' % (time_in, fmt_in)
        else:
            raise ChandraTimeError, "Invalid input format '%s'" % fmt_in
    else:
        match_style = None
        for ts_name in _keys_time_style:
            if re.match(time_style[ts_name]['match'], time_in):
                match_style = time_style[ts_name]
                break
        if match_style:
            ax3_fmt_in = match_style['ax3_fmt']
            ax3_sys_in = match_style['ax3_sys']
        else:
            raise ChandraTimeError, "Unknown format for input time '%s'" % time_in

    if sys_in:
        if sys_in in time_system:
            ax3_sys_in = time_system[sys_in]
        else:
            raise ChandraTimeError, "Invalid input system '%s'" % sys_in
        
    fmt_out = fmt_out or 'secs'
    if fmt_out in time_style:
        ax3_fmt_out = time_style[fmt_out]['ax3_fmt']
        ax3_sys_out = time_style[fmt_out]['ax3_sys']
    else:
        raise ChandraTimeError, "Invalid output format '%s'" % fmt_out

    if sys_out:
        if sys_out in time_system:
            ax3_sys_out = time_system[sys_out]
        else:
            raise ChandraTimeError, "Invalid output system '%s'" % sys_out

    if fmt_in == 'unix': time_in = str(float(time_in) - T1998)

    time_out = axTime3.convert_time(time_in,
                                    ax3_sys_in,
                                    ax3_fmt_in,
                                    ax3_sys_out,
                                    ax3_fmt_out,
                                    )

    if fmt_out == 'unix': time_out = str(float(time_out) + T1998)
    return time_out

class DateTime(object):
    """DateTime - Convert between various time formats

    """
    def __init__(self, time_in, format=None):
        self.time_in = time_in
        self.format  = format

    def __getattr__(self, fmt_out):
        if fmt_out not in time_style:
            raise ChandraTimeError, "Unknown output format '%s'" % fmt_out
            
        for sys_out, ax3_sys_out in time_system.items():
            if  time_style[fmt_out]['ax3_sys'] == ax3_sys_out: break

        time_out = convert(self.time_in,
                           fmt_in=self.format,
                           fmt_out=fmt_out,
                           sys_out=sys_out)
        try:
            time_out = time_style[fmt_out]['typecast'](time_out)
        except KeyError:
            pass

        return time_out
        
# 
# 1;
# 
# __END__
# 
# =head1 NAME
# 
# 
# 
# =head1 SYNOPSIS
# 
#   use Chandra::Time;
# 
#   # Create a Chandra::Time object
#   $t      = Chandra::Time->new('2002-05-28T01:02:03');
# 
#   # Do some converting
#   $date = $t->date;  # Convert 2002-05-28T01:02:03 to YYYY:DDD:HH:MM:SS
#   $secs = $t->secs;  # Time in CXC seconds (since 1998-01-01T00:00:00)
#   $unix = $t->unix;  # Unix time (since 1970 Jan 1, 0 UTC)
#   $unix = $t->unix('1998:241:02:14:12.233');  # Convert a different time
# 
#   # Make a Julian Date time object which only accepts JD as inputs
#   $t_jd  = Chandra::Time->new('2451161.5', {format => 'jd'});
#   $fits  = $t_jd->fits('1998:241:02:14:12.2');  # NOPE!
# 
# =head1 SEE ALSO
# 
# README.axTime3 and README.XTime
# 
# =head1 AUTHOR
# 
# Tom Aldcroft, E<lt>aldcroft@localdomainE<gt>
# 
# =head1 COPYRIGHT AND LICENSE
# 
# Copyright (C) 2005 by Tom Aldcroft
# 
# This library is free software; you can redistribute it and/or modify
# it under the same terms as Perl itself, either Perl version 5.8.3 or,
# at your option, any later version of Perl 5 you may have available.
# 
# 
# =cut
# 
