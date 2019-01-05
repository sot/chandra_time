//----------------------------------------------------------------------
//
//  RCS: $Id: axTime3.cc,v 1.2 2007-08-27 21:30:59 aldcroft Exp $
//
//  File:        axTime3.C
//  Programmer:  Arnold Rots  -  ASC
//  Date:        7 June 1999
//  Subsystem:   Utilities
//  Description: Time conversion utility using XTime.
//
// .NAME    axTime - Time conversion utility for AXAF
// .LIBRARY Util
// .HEADER  AXAF Time Converter
//
// .SECTION SYNOPSIS
//  .RI axTime3 time " " timeSystem(in) " " timeFormat(in) " " tS(out) " " tF(out)
//
// .SECTION Author
//  Arnold Rots,
//  USRA, ASC
//  <arots@xebec.gsfc.nasa.gov>
//
// .SECTION DESCRIPTION
//  axTime3 is a utility that performs conversions between different
//  time systems and formats.  A time is input on the command line in
//  any system and format, and may be retrieved in any system and format.
//  Optionally, a reference MJD may be specified, the default being
//  50814.0 TT (i.e., 1998.0 TT).
//
//  The supported time systems are: MET, TT, TAI, and UTC.  The codes are:
//  m[et], t[t], ta[i] or a, and u[tc].
//
//  The supported time formats are: seconds since 1994.0 in decimal
//  and hexadecimal format, Mission Day Number (ddd:hh:mm:ss.sss), Julian Day,
//  Modified Julian Day (=JD-2400000.5), Date (yyyy:ddd:hh:mm:ss.ss...),
//  Calendar Date (yyyyMondd at hh:mm:ss.ss...), and FITS-style date-time
//  string (yyyy-mm-ddThh:mm:ss.ss...).  The last three format codes may have
//  a digit appended to indicate the number of decimals requested in the
//  seconds field.
//  The codes are: s, h, n, j, d[n], c[n], and f[n].
//
//  The user is expected to provide the time to be converted on the command
//  line, with a time system and a time format specification for both input
//  and output.
//
//  Time system and time format codes may be abbreviated to single
//  characters and are case-insensitive.
//
//  A reference MJD may optionally be inserted between the specifications
//  of the input and output time system and time format, either as a single
//  number, or as an integer and fractional part (long and double).
//
// .VERSION $Revision $
//----------------------------------------------------------------------
//
static const char* const rcsid = "axTime $Id: axTime3.cc,v 1.2 2007-08-27 21:30:59 aldcroft Exp $" ;

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <limits.h>
#include "XTime.h"
using namespace std;

XTime *getinput (int, char **) ;
int getsys (XTime::TimeSys *) ;
int readsys (char *, XTime::TimeSys *) ;
int getform (XTime::TimeFormat *, int *, int *, int *) ;
int readform (char *, XTime::TimeFormat *, int *, int *, int *) ;

//
//   -------
// -- axTime --
//   -------
//<time_in> <ts_in> <tf_in> [[<MJDrefint>] MJDreffrac>] <ts_out> <tf_out>
//
//  time_in     String containing the time in time system ts_in, format tf_in
//  ts_in       Time system of input time
//  tf_in       Time format of input time
//    MJDrefint   Optional integer part of optional reference MJD [NOT ALLOWED]
//    MJDreffrac  Fractional part of optional reference MJD       [NOT ALLOWED]
//  ts_out      Time system of output time
//  tf_out      Time format of output time

void axTime3 (char *time_in,
	      char *ts_in,
	      char *tf_in,
	      char *ts_out,
	      char *tf_out,
	      char *time_out
	      ) {
  XTime *T ;
  int error = 0 ;
  XTime::TimeSys tSys ;
  XTime::TimeFormat tForm ;
  int hexfmt ;
  int nmday ;
  int dec = 0 ;
  int argc = 6;
  char *argv[6];
  
//  Errr, I don't know c anymore..  
  argv[0] = "convert_time";
  argv[1] = time_in;
  argv[2] = ts_in;
  argv[3] = tf_in;
  argv[4] = ts_out;
  argv[5] = tf_out;

//    Get the time
  if ( ( T = getinput(argc, argv) ) == NULL ) {
    sprintf(time_out, "Error: Incorrect time format; try again");
    error = 1 ;
  }

//    Conversion and output loop
  if ( !error ) {

//      Get desired time system
    if ( readsys (argv[argc-2], &tSys) ) {
      error = 2 ;
      sprintf(time_out, "Error: Failed readsys");
    }

    //      Get desired time format
    if ( readform (argv[argc-1], &tForm, &hexfmt, &nmday, &dec) ) {
      error = 3 ;
      sprintf(time_out, "Error: Failed readform");
    }

//      Convert and print the result
    if ( !error ) {
      switch (tForm) {
      case XTime::SECS : case XTime::JD : case XTime::MJD : {
	double t = T->get(tSys, tForm) ;
	if ( hexfmt ) {
	  unsigned int jt = (unsigned long) t ;
	  sprintf(time_out, "0x%7x", jt);
	  //	  cout << "0x" << setw(7) << hex << jt ;
	}
	else if ( nmday ) {
	  int day = (int) t / 86400 ;
	  t -= day * 86400 ;
	  int h = (int) t / 3600 ;
	  t -= h * 3600 ;
	  int m = (int) t / 60 ;
	  t -= m * 60 ;
	  sprintf(time_out, "%d:%d:%d:%.10f", day, h, m, t);
	  //	  cout << dec << day << ":" << h << ":" << m << ":"
	  //	       << setprecision(10) << t ;
	}
	else 
	  //	  cout << setprecision(18) << t ;
	  sprintf(time_out, "%.9f", t);
	break ;
      }
      case XTime::DATE : case XTime::CALDATE : case XTime::FITS : {
	const char *s = T->getDate(tSys, tForm, dec) ;
	sprintf(time_out, "%s", s);
	break ;
      }
      }
    }
    delete(T);
  }

  return ;
}

void _convert_time(char *time_in,
                    char *ts_in,
                    char *tf_in,
                    char *ts_out,
                    char *tf_out,
                    char *time_out  // passed in as a long blank string
    ) {
  axTime3(time_in, ts_in, tf_in, ts_out, tf_out, time_out);
}


//
//   ----------
// -- getinput --
//   ----------
//

// Description:
// Parse the input time on the command line.
XTime *getinput (int argc, char *argv[])
{
  XTime *tt = NULL ;
  char str[256] ;
  double t ;
  unsigned int jt = 0 ;
  XTime::TimeSys tSys = XTime::MET ;
  XTime::TimeFormat tForm = XTime::SECS ;
  int hexfmt = 0 ;
  int ch = 0 ;
  int getform = 0 ;
  int error = 0 ;
  int nmday = 0 ;
  int day = 0 ;
  int h = 0 ;
  int m = 0 ;
  int dec = 0 ;
  long mjdi = 0 ;
  double mjdf = 0.0 ;

//    No time argument
  if ( argc < 2 )
    error = 1 ;

  if ( !error ) {

//    Only time provided
    if ( argc == 2 ) {
      if ( ( argv[1][4] == '-' ) && ( argv[1][7] == '-' ) ) {
	  strcpy (str, argv[1]) ;
	  tForm = XTime::FITS ;
	  ch = 1 ;
	}
      else if ( strstr (argv[1], ":") ) {
	sscanf (argv[1], "%d:", &day) ;
	if ( ( day < 1900 ) && ( day > 366 ) ) {
	  nmday = 1 ;
	  tForm = XTime::SECS ;
	}
	else {
	  strcpy (str, argv[1]) ;
	  tForm = XTime::DATE ;
	  ch = 1 ;
	}
      }
      else
	getform = 1 ;
    }
    else {
      int istrt = 2 ;
//      Caldate format?
      if ( ( argc >= 4 ) && ( !strcmp(argv[2], "at")
			     || !strcmp(argv[2], "AT") ) ) {
	istrt = 4 ;
	sprintf (str, "%s %s %s", argv[1], argv[2], argv[3]) ;
	tForm = XTime::CALDATE ;
	ch = 1 ;
      }

//      FITS or Date format?
      else if ( ( argv[1][4] == '-' ) && ( argv[1][7] == '-' ) ) {
	strcpy (str, argv[1]) ;
	tForm = XTime::FITS ;
	ch = 1 ;
      }
      else if ( strstr (argv[1], ":") ) {
	sscanf (argv[1], "%d:", &day) ;
	if ( ( day < 1900 ) && ( day > 366 ) ) {
	  nmday = 1 ;
	  tForm = XTime::SECS ;
	}
	else {
	  strcpy (str, argv[1]) ;
	  tForm = XTime::DATE ;
	  ch = 1 ;
	}
      }

//        Get time system
      if ( argc > istrt )
	error = readsys (argv[istrt], &tSys) ;
      
//        Get time format
      if ( !error ) {
	if ( argc > istrt+1 )
	  error = readform (argv[istrt+1], &tForm, &hexfmt, &nmday, &dec) ;
	else if ( !ch )
	  getform = 1 ;
      }
      if ( argc > istrt+4) {
	mjdi = atoi (argv[istrt+2]) ;
	if ( argc > istrt+5)
	  mjdf = atof (argv[istrt+3]) ;
      }
    }
  }

  if ( !error ) {

//    Number input
    if ( !ch ) {
      if ( hexfmt ) {
	sscanf (argv[1], "%x", &jt) ;
	t = jt ;
      }
      else if ( nmday ) {
	sscanf (argv[1], "%d:%d:%d:%lg", &day, &h, &m, &t) ;
	t += 86400 * day + 3600 * h + 60 * m ;
      }
      else
	t = atof (argv[1]) ;
//      If format has to be deduced ...
      if ( getform ) {
	if ( t < 100000.0 )
	  tForm = XTime::MJD ;
	else if ( t < 2500000.0 )
	  tForm = XTime::JD ;
	else
	  tForm = XTime::SECS ;
      }
      tt = new XTime (t, tSys, tForm, mjdi, mjdf) ;
    }

//    Character string input
    else
      tt = new XTime(str, tSys, tForm, mjdi, mjdf) ;
  }

//  Done
  return tt ;
}

//
//   ---------
// -- readsys --
//   ---------
//

// Description:
// Interpret the time system code provided by the user.
// Return 0 if valid code, -1 for quit, +1 for unrecognized code.
int readsys (char *tsys, XTime::TimeSys *tSys)
{
  int quit = 0 ;
  switch (*tsys) {
  case 'm': case 'M':
    *tSys = XTime::MET ;
    break ;
  case 't': case 'T':
    switch (tsys[1]) {
    case 'a': case 'A':
      *tSys = XTime::TAI ;
      break ;
    default:
      *tSys = XTime::TT ;
      break ;
    }
    break ;
  case 'a': case 'A':
    *tSys = XTime::TAI ;
    break ;
  case 'u': case 'U':
    *tSys = XTime::UTC ;
    break ;
  case 'q': case 'Q': case 'x': case 'X':
    quit = -1 ;
    break ;
  default:
    quit = 1 ;
  }
  return quit ;
}

//
//   ---------
// -- getform --
//   ---------
//

// Description:
// Get time format code from the user.
int getform (XTime::TimeFormat *tForm, int *hex, int *nmday, int *dec)
{
  int cont = 1 ;
  char tform[32] ;

  while ( cont > 0 ) {
    cout << "Print in Format SECS, HEXSECS, NUMDAY, JD, MJD, DATE, CALDATE, FITS, Dn, Cn, Fn, or Quit: " ;
    char* fgets_value = fgets (tform, 10, stdin) ;
    cont = readform (tform, tForm, hex, nmday, dec) ;
  }
  return cont ;
}

//
//   ----------
// -- readform --
//   ----------
//

// Description:
// Interpret the time format code provided by the user.
// Return 0 if valid code, -1 for quit, +1 for unrecognized code.
int readform (char *tform, XTime::TimeFormat *tForm,
	      int *hex, int *nmday, int *dec)
{
  int quit = 0 ;
  *hex = 0 ;
  *nmday = 0 ;

  switch (*tform) {
  case 's': case 'S':
    *tForm = XTime::SECS ;
    break ;
  case 'j': case 'J':
    *tForm = XTime::JD ;
    break ;
  case 'm': case 'M':
    *tForm = XTime::MJD ;
    break ;
  case 'd': case 'D':
    *tForm = XTime::DATE ;
    break ;
  case 'c': case 'C':
    *tForm = XTime::CALDATE ;
    break ;
  case 'f': case 'F':
    *tForm = XTime::FITS ;
    break ;
  case 'h': case 'H':
    *tForm = XTime::SECS ;
    *hex = 1 ;
    break ;
  case 'n': case 'N':
    *tForm = XTime::SECS ;
    *nmday = 1 ;
    break ;
  case 'q': case 'Q': case 'x': case 'X':
    quit = -1 ;
    break ;
  default:
    quit = 1 ;
  }
  switch (*tForm) {
  case XTime::DATE: case XTime::CALDATE: case XTime::FITS:
    if ( ( tform[1] > 47 ) && ( tform[1] < 58 ) )
      sscanf (tform+1, "%d", dec) ;
    else
      *dec = 0 ;
    break ;
  default:
    break ;
  }
  return quit ;
}

