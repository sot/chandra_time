//----------------------------------------------------------------------
//
//
//  File:        XTime.C
//  Programmer:  Arnold Rots  -  USRA/SAO
//  Date:        7 June 1999
//  Subsystem:   XFF
//  Library:     ObsCat
//  Description: Code for XTime, XTimeRange, XTRList classes
//
//----------------------------------------------------------------------
//

#include <string.h>
#include <ctype.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <iostream>
#include "XTime.h"
#define TAIUTC "tai-utc.dat"

using namespace std;

int          XTime::NUMOBJECTS  =       0       ; // Number of instantiated XTime objects
const double XTime::MJD0        = 2400000.5     ; // JD - MJD
const long   XTime::MJD1972     =   41317       ; // MJD at 1972
const double XTime::DAY2SEC     =   86400.0     ; // Seconds per day
const double XTime::SEC2DAY     = 1.0 / DAY2SEC ; // Inverse seconds per day
const long   XTime::MJDREFint   =   50814       ; // MJD at 1998.0
const double XTime::MJDREFfr    =       0.0     ; // MJD at 1998.0
const double XTime::REFLEAPS    =      31.0     ;  // Leap seconds at default MJDREF (1998.0 TT)
const double XTime::TAI2TT      =      32.184   ; // TT - TAI
int    XTime::NUMLEAPSECS = 0 ;      // Leap seconds: 1972 through 2009
long   XTime::LEAPSMJD[]  = {41317, 41499, 41683, 42048, 42413, 42778, 43144, 43509, 43874,
			     44239, 44786, 45151, 45516, 46247, 47161, 47892, 48257, 48804,
			     49169, 49534, 50083, 50630, 51179, 53736, 54832, 56109} ;
double XTime::LEAPSECS[]  = {10, 11, 12,13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
			     26, 27, 28, 29, 30, 31, 32, 33, 34, 35} ;
time_t XTime::WALLCLOCK0      ;      // Wallclock time when leap seconds were read

static int daymonth[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31} ;
static const char*  const month[12] = {"Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"} ;

//
//   ------------------------
// -- XTime::setleaps (void) --
//   ------------------------
//

// Description:
// Function to set leap second table
// If it was more than abs(dt) seconds since the
// leap seconds were read, the leap second table
// is refreshed; if dt > 0, only additional leap
// seconds are added; if dt < 0, all leap seconds
// are refreshed.  The default is dt=5000000 (about
// two months).
// This is the private method; for the public method
// use void XTime::setLeaps (double dt).

void XTime::setleaps (double dt)
{
  // Increment the object counter:
  NUMOBJECTS++ ;

  // Now the business of the leap seconds
  int refresh = 0 ;
  int all = dt < 0.0 ;
  if ( all ) dt = -dt ;
  // If they were set before, check whether they expired
  if ( NUMLEAPSECS ) {
    time_t wallclock1 ;
    time (&wallclock1) ;
    if ( difftime (wallclock1, WALLCLOCK0) > dt )
      refresh = 1 ;
  }
  else
    refresh = 1 ;

  // Try to read the leap seconds file
  if ( refresh ) {
    char *filepath ;
    FILE *FF = NULL ;
    char lsfile[256] ;
    int nums = 0 ;

    // Did the user provide his/her own?
    if ( filepath = getenv("TIMING_DIR") ) {
      sprintf (lsfile, "%s/%s", filepath, TAIUTC) ;
      FF = fopen (lsfile, "r") ;
    }

    // Otherwise, the standard file
    if ( FF == NULL )
      if ( filepath = getenv ("ASC_DATA") ) {
	sprintf (lsfile, "%s/%s", filepath, TAIUTC) ;
	FF = fopen (lsfile, "r") ;
      }

    // If the file is found, read it (only post 1972)
    if ( FF ) {
      long leapsMD ;
      double leapsecs ;
      int i ;
      while ( fscanf (FF, "%d %*s  1 =JD 24%ld.5 %*s %lg S + (MJD - %*lg) X %*lg %*s",
		      &i, &leapsMD, &leapsecs) == 3 ) {
	if ( i > 1970 ) {
	  // Only overwrite existing values when forced to do so
	  if ( all || ( nums >= NUMLEAPSECS ) ) {
	    LEAPSMJD[nums] = leapsMD ;
	    LEAPSECS[nums] = leapsecs ;
	    nums++ ;
	  }
	}
      }
      int error = ferror (FF) ;
      fclose (FF) ;
      // If we got fewer leap seconds than before, there must have been an error
      if ( ( nums >= NUMLEAPSECS ) && !error ) {
	time (&WALLCLOCK0) ;
	NUMLEAPSECS = nums ;
      }
    }

    // File could not be found; use the ones we know about when coding
    else if ( !NUMLEAPSECS ) {
      nums = 26 ;                 // Leap seconds: 1972.0 through 2013.0
      NUMLEAPSECS = nums ;
    }

  }
  return ;
}

//
//   -------------------------------------------------------------
// -- XTime::setmyleaps (double *leapval, long mjdi, double mjdf) --
//   -------------------------------------------------------------
//

// Description:
// Set the number of leap seconds for time mjdi+mjdf (TT) in leapval.
// mjdf should include timeZero, if applicable.
// Return 1 if mjdi+mjdf falls during a leap second; otherwise 0.
int XTime::setmyleaps (double *leapval, long mjdi, double mjdf)
{
  int i = NUMLEAPSECS - 1 ;
  int m = 0 ;
  double x = (double) mjdi + mjdf - TAI2TT * SEC2DAY ;
  long j = (long) x ;
  while ( ( j < LEAPSMJD[i] ) && i )
    i-- ;
  if ( ( (x - LEAPSECS[i]*SEC2DAY) < LEAPSMJD[i] ) && i ) {
    i-- ;
    if ( (LEAPSMJD[i+1] - x) <= SEC2DAY )
      m = 1 ;
  }
  *leapval = LEAPSECS[i] ;
  return m ;
}

//
//   ---------------------------------------------------------------------------
// -- XTime::set (double tt, TimeSys ts, TimeFormat tf, long mjdi, double mjdf) --
//   ---------------------------------------------------------------------------
//

// Description:
// General set function; tt sets time in SECS, MJD, or JD, as
// specified by ts and tf.  Allows for setting MJDREF
// (mjdi+mjdf); the default is 50814.0 (1998.0 TT).  The default
// for ts is MET, for tf SECS.  The defaults for mjdi and mjdf
// are 0 and 0.0.  Note that if a new MJDref is specified
// (non-zero), it will be assumed to be in Time System ts.
// I.e., set (x, UTC, SECS) is not the same as set
// (x, UTC, SECS, 50814)
// This method calls
// XTime::set (long, double, TimeSys, TimeFormat, long, double)
void XTime::set (double tt, TimeSys ts, TimeFormat tf,
		 long mjdi, double mjdf)
{
  double x ;
  long k ;

  k = (long) tt ;
  x = tt - k ;
  set (k, x, ts, tf, mjdi, mjdf) ;

  return ;
}

//
//   --------------------------------------------------------------------------------------
// -- XTime::set (long tti, double ttf, TimeSys ts, TimeFormat tf, long mjdi, double mjdf) --
//   --------------------------------------------------------------------------------------
//

// Description:
// Most general set function.  tti+ttf sets time in SECS, MJD, or
// JD, as specified by ts and tf.  Allows for setting MJDREF
// (mjdi+mjdf); the default is 50814.0 (1998.0 TT).
// The default for ts is TT, for tf MJD.  The defaults for mjdi
// and mjdf are 0 and 0.0.
// Note that if a new MJDref is specified (non-zero), it will be
// assumed to be in Time System ts.
// I.e., set (k, x, UTC, SECS) is not the same as
// set (k, x, UTC, SECS, 50814)
void XTime::set (long tti, double ttf, TimeSys ts, TimeFormat tf,
		 long mjdi, double mjdf)
{
  double total, x ;
  long j=0, k ;
  int i ;
  leapflag = 0 ;

  // First, set the MJDREF, if specified
  if ( mjdi > 1 ) {
    switch (ts) {
    case UTC: {
      XTime mt (mjdi, mjdf, ts) ;
      mt.mjd (&mjdi, &mjdf) ;
      break ;
    }
    case TAI:
      mjdf += TAI2TT * SEC2DAY ;
      if ( mjdf < 0.0 ) {
	mjdf++ ;
	mjdi-- ;
      }
      break ;
    }
    MJDrefint = mjdi ;
    MJDreffr = mjdf ;
    setmyleaps (&refLeaps, mjdi, mjdf) ;
  }

  // total contains the corrections wrt to TT in seconds
  total = 0.0 ;

  // Convert the format to MJD (TT); store in k and x
  switch (tf) {

    // First JD and MJD
  case JD:
    tti -= (long) MJD0 ;
    ttf -= 0.5 ;
  case MJD:
    k = tti ;
    x = ttf ;

    // Build up the corrections to TT, depending on ts
    switch (ts) {
    case UTC:
      i = NUMLEAPSECS - 1 ;
      while ( ( k < LEAPSMJD[i] ) && i ) {
	i-- ;
      }
      if ( ( i < NUMLEAPSECS-1 ) && ( k+1 == LEAPSMJD[i+1] ) &&
          ( (LEAPSMJD[i+1] - k + x + timeZero) < SEC2DAY  ) && i ) {
	i-- ;
	leapflag = 1 ;
      }
      total += LEAPSECS[i] ;
      myLeaps = LEAPSECS[i] ;
    case TAI:
      total += TAI2TT ;
    case TT:
    case MET:
      break ;
    default:                //  Error in ts; do nothing
      return ;
    }
    break ;

    // Seconds is slightly different since it's relative
    // Be careful about precision
  case SECS:
    k = (long) ((double) tti * SEC2DAY) ;
    x = (double) tti * SEC2DAY - k ;
    x += ttf * SEC2DAY + MJDreffr ;
    k += MJDrefint ;
    // Corrections are only needed for UTC, since the reference is now TT
    switch (ts) {
    case UTC:
      // First, subtract the leap seconds for the reference
      total -= refLeaps ;
      // Then add the leap seconds for the time itself
      i = NUMLEAPSECS - 1 ;
      j = (long) (k + x + timeZero) ;
      while ( ( j < LEAPSMJD[i] ) && i ) {
	i-- ;
      }
      if ( ( (k + x + timeZero - LEAPSMJD[i]) < SEC2DAY  ) && i ) {
	i-- ;
	leapflag = 1 ;
      }
      total += LEAPSECS[i] ;
      myLeaps = LEAPSECS[i] ;
    case TAI:
    case TT:
    case MET:
      break ;
    default:                //  Error in ts; do nothing
      return ;
    }
    break ;
  default:                //  Error in tf; do nothing
    return ;
  }

  // Now we are ready to set the time
  x += total * SEC2DAY ;
  j = (long) x ;
  MJDint = k + j ;
  MJDfr = x - j ;
  if ( MJDfr < 0.0 ) {
    MJDfr++ ;
    MJDint-- ;
  }
  // The leap seconds value and flag have already been set for UTC
  if ( ts != UTC )
    leapflag = setmyleaps (&myLeaps, MJDint, MJDfr+timeZero) ;

  return ;
}

//
//   ----------------------------------------------------------------------------
// -- XTime::set (char* date, TimeSys ts, TimeFormat tf, long mjdi, double mjdf) --
//   ----------------------------------------------------------------------------
//

// Description:
// General set function from a date string.
// Allows specification of DATE, CALDATE, or FITS formats.
// The defaults for ts, tf, and dec are UTC, DATE, and 0.
// This method calls
// XTime::set (long, double, TimeSys, TimeFormat, long, double)
void XTime::set (const char* date, TimeSys ts, TimeFormat tf,
		 long mjdi, double mjdf)
{
  long year=0, day=0, hour=0, minute=0 ;
  double second=0.0 ;
  int n ;
  int m = 0 ;
  char mn[4] ;

  switch (tf) {
  case DATE:
    n = sscanf (date, "%ld:%ld:%ld:%ld:%lg", &year, &day, &hour, &minute, &second) ;
    if ( n != 5 )
      return ;
    break ;
  case CALDATE:
    n = sscanf (date, "%ld%c%c%c%ld at %ld:%ld:%lg",
    &year, mn, mn+1, mn+2, &day, &hour, &minute, &second) ;
    if ( n != 8 )
      return ;
    if ( year%4 )
      daymonth[1] = 28 ;
    else
      daymonth[1] = 29 ;
    mn[0] = toupper(mn[0]) ;
    mn[1] = tolower(mn[1]) ;
    mn[2] = tolower(mn[2]) ;
    mn[3] = 0 ;
    while ( strcmp(mn, month[m]) ) {
      if ( m > 11 )
	return ;
      day += daymonth[m++] ;
    }
    break ;
  case FITS: {
    n = sscanf (date, "%ld-%d-%ldT%ld:%ld:%lg",
		&year, &m, &day, &hour, &minute, &second) ;
    if ( ( n != 6 ) && ( n != 3 ) )
      return ;
    if ( year%4 )
      daymonth[1] = 28 ;
    else
      daymonth[1] = 29 ;
    m-- ;
    for (int i=0; i<m; i++)
      day += daymonth[i] ;
    break ;
  }
  default:
    return ;
  }

  day += (year - 1972) * 365 - 1 ;
  day += (year - 1969) / 4 ;
  day += MJD1972 ;
  second += (double) hour * 3600 + minute * 60 ;
  second *= SEC2DAY ;

  set (day, second, ts, MJD, mjdi, mjdf) ;

  return ;
}

//
//   -------------------------------------------------
// -- XTime::monDay (const char* date, TimeFormat tf) --
//   -------------------------------------------------
//

// Description:
// Convert UTC or TT date string to calendar date string
const char* XTime::monDay (const char* date, TimeFormat tf) {
  char d[32] ;
  int year, day ;
  int m = 0 ;

  strcpy (d, date) ;
  sscanf (d, "%d:%d", &year, &day) ;
  if ( year%4 )
    daymonth[1] = 28 ;
  else
    daymonth[1] = 29 ;

  while ( day > daymonth[m] ) {
    day -= daymonth[m] ;
    m++ ;
  }
  if ( tf == CALDATE ) {
    sprintf (tdate, "%04d%s%02d at ", year, month[m], day) ;
    strcpy (tdate+13, d+9) ;
  }
  else if ( tf == FITS ) {
    sprintf (tdate, "%04d-%02d-%02dT", year, m+1, day) ;
    strcpy (tdate+11, d+9) ;
  }

  return ( tdate ) ;
}

//
//   ----------------------------------------
// -- XTime::get (TimeSys ts, TimeFormat tf) --
//   ----------------------------------------
//

// Description:
// Generalized time return function; returns SECS
// (relative to current MJDref), MJD, or JD, as
// specified by ts and tf.
// Default for ts is TT, for tf SECS.
double XTime::get (TimeSys ts, TimeFormat tf) const {
  double tt=timeZero ;
  
  switch (tf) {
  case SECS:
    switch (ts) {
    case UTC:
      tt = getUTC () ;
      break ;
    case TT:
      tt = getTT () ;
      break ;
    case TAI:
      tt = getTAI () ;
      break ;
    case MET:
      tt = getMET () ;
      break ;
    }
    break ;
  case JD:
    tt += MJD0 ;
  case MJD:
    switch (ts) {
    case UTC:
      tt -= myLeaps * SEC2DAY ;
    case TAI:
      tt -= TAI2TT * SEC2DAY ;
    case MET:
    case TT:
      tt += MJDint + MJDfr ;
      break ;
    }
  }
  return tt ;
}

//
//   ---------------------------------------------------
// -- XTime::mjd (long *mjdi, double *mjdf, TimeSys ts) --
//   ---------------------------------------------------
//

// Description:
// Return MJD (*mjdi+*mjdf) and put integer and fractional parts
// in arguments, for TimeSys ts (default: TT).
double XTime::mjd (long *mjdi, double *mjdf, TimeSys ts) const {

  switch (ts) {
  case TT:
    return TTmjd (mjdi, mjdf) ;
  case TAI:
    return TAImjd (mjdi, mjdf) ;
  case UTC:
    return UTmjd (mjdi, mjdf) ;
  }
  return 0.0;
}

//
//   -----------------------------------------
// -- XTime::UTmjd (long *mjdi, double *mjdf) --
//   -----------------------------------------
//

// Description:
// Return UTC MJD and put integer and fractional parts in
// arguments.
double XTime::UTmjd (long *mjdi, double *mjdf) const {
  long k = MJDint ;
  double x = MJDfr + timeZero - (TAI2TT+myLeaps)*SEC2DAY ;

  if ( x < 0.0 ) {
    x++ ;
    k-- ;
  }
  else if ( x >= 1.0 ) {
    x-- ;
    k++ ;
  }

  *mjdi = k ;
  *mjdf = x ;
  double tt = k + x ;

  return tt ;
}

//
//   -----------------------------------------------------
// -- XTime::getDate (TimeSys ts, TimeFormat tf, int dec) --
//   -----------------------------------------------------
//

// Description:
// Generalized date string return function.
// Allows specification of DATE, CALDATE, or FITS formats
// and the number of decimals in the seconds field.
// The defaults for ts, tf, and dec are UTC, DATE, and 0.
const char* XTime::getDate (TimeSys ts, TimeFormat tf, int dec) {
  long k ;
  double x ;

  // Get MJD representation
  mjd (&k, &x, ts) ;
  if ( ( ts == UTC ) && leapflag )
    x -= SEC2DAY ;
  while ( x < 0.0 ) {
    x++ ;
    k-- ;
  }
  while ( x >= 1.0 ) {
    x-- ;
    k++ ;
  }

  // Divide into year/day/hour/minute/second
  int year, day, hour, minute ;
  double second ;
  double dsec ;
  dsec = 0.5 * pow(10.0, (double) -dec) ;

  // First add dsec; later subtract it; this is to avoid rounding 59.9999 to 60.0
  day = k - MJD1972 ;
  second = x * DAY2SEC + dsec ;
  int i = 0 ;
  year = 1972 ;
  if ( ( ts == UTC ) && leapflag ) {
    second++ ;
    hour = (int) second / 3600 ;
    if ( hour > 23 ) hour-- ;
    second -= hour * 3600.0 ;
    minute = (int) second / 60 ;
    if ( minute > 59 ) minute-- ;
    second -= minute * 60.0 ;
  }
  else {
    hour = (int) second / 3600 ;
    second -= hour * 3600.0 ;
    minute = (int) second / 60 ;
    second -= minute * 60.0 ;
  }
  if ( hour > 23 ) {
    hour -= 24 ;
    day++ ;
  }
  second -= dsec ;
  if ( second < 0.0 ) second = 0.0 ;
  day++ ;
  while ( day > 365 ) {
    if ( !i ) {
      if ( day == 366 )
	break ;
      else
	day-- ;
    }
    day -= 365 ;
    year++ ;
    i = (i+1)%4 ;
  }

  char formt[32], f2[10] ;
  if ( dec ) {
    strcpy (formt, "%4d:%03d:%02d:%02d:%0") ;
    sprintf (f2, "%d.%df", dec+3, dec) ;
    strcat (formt, f2) ;
  }
  else
    strcpy (formt, "%4d:%03d:%02d:%02d:%02.0f") ;
  sprintf (tdate, formt,
	   year, day, hour, minute, second) ;
  /*
  switch (ts) {
  case TT:
    strcat (tdate, "TT") ;
    break ;
  case UTC:
    strcat (tdate, "UTC") ;
    break ;
  case MET:
    strcat (tdate, "MET") ;
    break ;
  default:
    break ;
  }
  */
  if ( ( tf == CALDATE ) || ( tf == FITS ) )
    return ( monDay (tdate, tf) ) ;
  else
    return tdate ;
}

//
//   -------------------------
// -- XTimeRange::setEmpty () --
//   -------------------------
//

// Description:
// Determine whether range is empty
void XTimeRange::setEmpty (void) {
  double t1=start.getMET() ;
  double t2=stop.getMET() ;
  if ( ( t1 >= t2 ) || ( t1 <= 0.0 ) || ( t2 <= 0.0 ) )
    empty = 1 ;
  else
    empty = 0 ;
  return ;
}

//
//   ---------------------------
// -- XTimeRange::printRange () --
//   ---------------------------
//

// Description:
// A two-liner in UTC date format
void XTimeRange::printRange (void) {
  cout << "---XTimeRange - Empty: " << empty
       << ", Start: " << start.getMET() << " (" << UTStartDate () << ")\n"
       << "                       "
       << "  Stop:  " << stop.getMET() << " (" << UTStopDate () << ")\n" ;
  return ;
}
//
//   ------------------------------
// -- XTimeRange::printRangeCal () --
//   ------------------------------
//

// Description:
// A two-liner in UTC calendar date format
void XTimeRange::printRangeCal (void) {
  cout << "---XTimeRange - Empty: " << empty
       << ", Start: " << start.getMET() << " (" << start.UTCalDate () << ")\n"
       << "                       "
       << "  Stop:  " << stop.getMET() << " (" << stop.UTCalDate () << ")\n" ;
  return ;
}

//
//   -----------------------
// -- XTRList::printList () --
//   -----------------------
//

// Description:
// Print list contents in UTC calendar date format
void XTRList::printList (void) {
  cout << "\nXTRList - Empty: " << empty << ", Number of ranges:: " << numXTRs
       << ", List range:\n" ;
  listRange.printRange () ;
  if ( numXTRs ) {
    cout << "Member ranges:\n" ;
    for (int i=0;i<numXTRs;i++)
      tr[i].printRange () ;
  }
  return ;
}

//
//   --------------------------
// -- XTRList::printListCal () --
//   --------------------------
//

// Description:
// Print list contents in UTC calendar date format
void XTRList::printListCal (void) {
  cout << "\nXTRList - Empty: " << empty << ", Number of ranges:: " << numXTRs
       << ", List range:\n" ;
  listRange.printRangeCal () ;
  if ( numXTRs ) {
    cout << "Member ranges:\n" ;
    for (int i=0;i<numXTRs;i++)
      tr[i].printRangeCal () ;
  }
  return ;
}

//
//   ----------------------------
// -- XTRList::XTRList (XTRList) --
//   ----------------------------
//

// Description:
// Copy constructor for a new TR list
XTRList::XTRList (const XTRList &trl)
{
  numXTRs = trl.numXTRs ;
  listRange = trl.listRange ;
  empty = trl.empty ;
  tr = new XTimeRange[numXTRs] ;
  for (int i=0; i<numXTRs; i++)
    tr[i] = trl.tr[i] ;
  return ;
}

//
//   ------------------------------
// -- XTRList::operator= (XTRList) --
//   ------------------------------
//

// Description:
// Copy operator for a TR list
XTRList& XTRList::operator= (const XTRList &trl)
{
  delete [] tr ;
  numXTRs = trl.numXTRs ;
  listRange = trl.listRange ;
  empty = trl.empty ;
  tr = new XTimeRange[numXTRs] ;
  for (int i=0; i<numXTRs; i++)
    tr[i] = trl.tr[i] ;
  return *this ;
}


//
//   -------------------------------------
// -- XTRList::XTRList (XTRList, XTRList) --
//   -------------------------------------
//

// Description:
// Construct a new TR list by "AND"ing two existing lists
XTRList::XTRList (const XTRList &trl1, const XTRList &trl2)
  : numXTRs (1), empty (1), tr (0) {

//  Trivial cases: if one of them is empty, the result is empty

  if ( trl1.isEmpty() || trl2.isEmpty() ) {
    numXTRs = 1 ;
    empty = 1 ;
    tr = new XTimeRange () ;
    listRange = *tr ;
    return ;
  }

//  To minimize work, make sure the second one is the shortest

  const XTRList* list1 = &trl1 ;
  const XTRList* list2 = &trl2 ;
  int nlist1 = list1->numXTRs ;
  int nlist2 = list2->numXTRs ;
  if ( nlist1 < nlist2 ) {
    int i = nlist2 ;
    nlist2 = nlist1 ;
    nlist1 = i ;
    list1 = list2 ;
    list2 = &trl1 ;
  }

//  Simple case: second list has only one member

  if ( nlist2 == 1 ) {
    XTRList scratchlist (*list1) ;
    scratchlist.andRange ( list2->tr[0] ) ;
    numXTRs = scratchlist.numXTRs ;
    listRange = scratchlist.listRange ;
    empty = scratchlist.empty ;
    tr = new XTimeRange[numXTRs] ;
    for (int i=0; i<numXTRs; i++)
      tr[i] = scratchlist.tr[i] ;
    return ;
  }

//  The full works: AND each range in list2 with all of list1
//                  OR the resulting lists

  XTRList buildlist ;
  int i ;
  for (i=0;i<nlist2;i++) {
    XTRList scratchlist (*list1) ;
    scratchlist.andRange ( list2->tr[i] ) ;
    buildlist.orList (scratchlist) ;
  }
  numXTRs = buildlist.numXTRs ;
  listRange = buildlist.listRange ;
  empty = buildlist.empty ;
  tr = new XTimeRange[numXTRs] ;
  for (i=0; i<numXTRs; i++)
    tr[i] = buildlist.tr[i] ;
  return ;
}

//
//   -----------------------------
// -- XTRList::isInRange (XTime&) --
//   -----------------------------
//

// Description:
// Return 0 if in range
int XTRList::isInRange (const XTime &T) const {
  for (int i=0;i<numXTRs;i++)
    if ( !tr[i].isInRange (T) )
      return 0 ;
  return 1 ;
}

//
//   -----------------------------
// -- XTRList::isInRange (double) --
//   -----------------------------
//

// Description:
// Return 0 if in range
int XTRList::isInRange (double t) const {
  for (int i=0;i<numXTRs;i++)
    if ( !tr[i].isInRange (t) )
      return 0 ;
  return 1 ;
}

//
//   ----------------------------
// -- XTRList::getRange (XTime&) --
//   ----------------------------
//

// Description:
// Return range in which XTime object <T> falls
const XTimeRange* XTRList::getRange (const XTime &T) const {
  for (int i=0;i<numXTRs;i++)
    if ( !tr[i].isInRange (T) )
      return tr+i ;
  return NULL ;
}

//
//   ----------------------------
// -- XTRList::getRange (double) --
//   ----------------------------
//

// Description:
// Return range in which MET time <t> falls
const XTimeRange* XTRList::getRange (double t) const {
  for (int i=0;i<numXTRs;i++)
    if ( !tr[i].isInRange (t) )
      return tr+i ;
  return NULL ;
}

//
//   -----------------------
// -- XTRList::totalTime () --
//   -----------------------
//

// Description:
// Return total time (in seconds), covered by the list
double XTRList::totalTime (void) const {
  double tt = 0.0 ;
  if ( !empty )
    for (int i=0;i<numXTRs;i++)
      tt += tr[i].totalTime () ;
  return tt ;
}

//
//   -----------------
// -- XTRList::orList --
//   -----------------
//

// Description:
// "OR" in another XTime Range List
void XTRList::orList (const XTRList &trl) {

//  Do nothing if trl is empty

  if ( trl.empty )
    return ;

//  If *this is empty, replace it by trl

  if ( empty ) {
    delete [] tr ;
    numXTRs = trl.numXTRs ;
    listRange = trl.listRange ;
    empty = trl.empty ;
    tr = new XTimeRange[numXTRs] ;
    for (int i=0; i<numXTRs; i++)
      tr[i] = trl.tr[i] ;
  }

//  Do the full thing

  else {
    int n = trl.numXTRs ;
    for (int i=0;i<n;i++)
      orRange ( trl.tr[i] ) ;
  }
  return ;
}

//
//   ------------------
// -- XTRList::notList --
//   ------------------
//

// Description:
// Negate a XTime Range List over a specified time range
void XTRList::notList (const XTimeRange &T) {

//  If the list was empty, the answer is just T ...

  if ( empty ) {

//  ... unless, of course, T was empty, too, in which case nothing changes

    if ( !T.isEmpty() ) {
      *tr = T ;
      listRange = T ;
      numXTRs = 1 ;
      empty = 0 ;
    }
  }

//  "Regular" case

  else {
    XTimeRange* ntr = new XTimeRange[numXTRs+1] ;
    ntr[0].setStart(1000.0) ;
    for (int i=0; i<numXTRs; i++) {
      ntr[i].setStop(tr[i].TStart()) ;
      ntr[i+1].setStart(tr[i].TStop()) ;
    }
    ntr[numXTRs].setStop(1.0e20) ;
    numXTRs++ ;
    delete [] tr ;
    tr = ntr ;
    setListRange () ;
    andRange (T) ;
  }
  return ;
}


//
//   -------------------
// -- XTRList::andRange --
//   -------------------
//

// Description:
// "AND" in an extra XTime Range
void XTRList::andRange (const XTimeRange &T) {
  int startin=0, stopin=0 ;
  int startafter=0, stopafter=0 ;
  int zap=0 ;
  int istart, istop ;
  int i ;
  double tstart = T.METStart () ;
  double tstop = T.METStop () ;
//
//  First the trivial cases
//
  if ( empty )
    return ;
  else if ( T.isEmpty () )
    zap = 1 ;
  else if ( ( tstart <= listRange.METStart () ) &&
      ( tstop >= listRange.METStop () ) )
    return ;
  else if ( tstop < listRange.METStart () )
    zap = 1 ;
  else if ( tstart > listRange.METStop () )
    zap = 1 ;
//
//  See where the start and stop times fall in the existing list
//  (add 1 to the indices)
  else {
    for (i=0;i<numXTRs;i++) {
      if ( !startin ) {
	istart = tr[i].isInRange (tstart) ;
	if ( !istart )
	  startin = i + 1 ;
	else if ( istart > 0 )
	  startafter = i + 1 ;
      }
      if ( !stopin ) {
	istop = tr[i].isInRange (tstop) ;
	if ( !istop )
	  stopin = i + 1 ;
	else if ( istop > 0 )
	  stopafter = i + 1 ;
      }
    }
//
//  Now figure out what to do
//    Which range do we start in?
//
    if ( startin ) {
      startin -- ;                     // Correct the index
      tr[startin].setStart (tstart) ;  // Adjust the time
    }

//      In between
    else if ( !stopin && ( startafter == stopafter ) )
      zap = 1 ;

//      Start after
    else
      startin = startafter ;

//    Which range do we stop in?
    if ( !zap ) {
      if ( stopin ) {
	stopin-- ;
	tr[stopin].setStop (tstop) ;
      }

//      Stop after
      else
	stopin = stopafter - 1 ;
    }
  }

//
//  Calculate the new length
  int newNumXTRs ;
  if ( zap ) {
    newNumXTRs = 1 ;
    empty = 1 ;
  }
  else
    newNumXTRs = stopin - startin + 1 ;

//  No change in number of ranges: done
  if ( numXTRs == newNumXTRs ) {
    if ( zap )
      tr->resetRange (0.0, 0.0) ;
    setListRange () ;
    return ;
  }

//
//  Make a new set of ranges
  XTimeRange* newXTR = new XTimeRange[newNumXTRs] ;

//
//    Rearrange the ranges
  if ( !zap ) {
//      Now copy the remaining ones
    int j=0 ;
    for (i=startin;i<=stopin;i++,j++)
      newXTR[j] = tr[i] ;
  }
  else
    newXTR->resetRange (0.0, 0.0) ;

//
//  Exchange the two lists
  delete [] tr ;
  tr = newXTR ;
  numXTRs = newNumXTRs ;
  setListRange () ;

  return ;
}

//
//   ------------------
// -- XTRList::orRange --
//   ------------------
//

// Description:
// "OR" in an extra XTime Range
void XTRList::orRange (const XTimeRange &T) {
  int startin=0, stopin=0 ;
  int startafter=0, stopafter=0 ;
  int before=0, after=0, between=0, straddle=0 ;
  int istart, istop ;
  int i ;
  double tstart = T.METStart () ;
  double tstop = T.METStop () ;

//
//  Handle the empties first
//
  if ( T.isEmpty () )
    return ;
  if ( empty ) {
    numXTRs = 1 ;
    empty = 0 ;
    tr[0] = T ;
    listRange = T ;
    return ;
  }

//
//  First the trivial cases
//
  if ( ( tstart <= listRange.METStart () ) &&
      ( tstop >= listRange.METStop () ) )
    straddle = 1 ;
  else if ( tstop < listRange.METStart () )
    before = 1 ;
  else if ( tstart > listRange.METStop () )
    after = 1 ;

//
//  See where the start and stop times fall in the existing list
//  (add 1 to the indices)
  else {
    for (i=0;i<numXTRs;i++) {
      if ( !startin ) {
	istart = tr[i].isInRange (tstart) ;
	if ( !istart )
	  startin = i + 1 ;
	else if ( istart > 0 )
	  startafter = i + 1 ;
      }
      if ( !stopin ) {
	istop = tr[i].isInRange (tstop) ;
	if ( !istop )
	  stopin = i + 1 ;
	else if ( istop > 0 )
	  stopafter = i + 1 ;
      }
    }
//
//  Now figure out what to do
//    Which range do we start in?
//
    if ( startin ) {
      if ( startin == stopin )  // If we're stopping in the same one, return
	return ;
      startin -- ;              // Correct the index
    }

//      In between
    else if ( !stopin && ( startafter == stopafter ) )
      between = stopafter ;

//      Somebody's start time needs to be adjusted
    else {
      startin = startafter ;
      tr[startin].setStart (tstart) ;
    }

//    Which range do we stop in?
    if ( stopin )
      stopin-- ;
//      Somebody's stop time needs to be adjusted
    else
      if ( stopafter ) {
	stopin = stopafter - 1 ;
	tr[stopin].setStop (tstop) ;
      }
  }

//
//  The range list must now be non-empty
  empty = 0 ;

//
//  Calculate the new length
  int newNumXTRs ;
  if ( before + after + between )
    newNumXTRs = numXTRs + 1 ;
  else if ( straddle )
    newNumXTRs =  1;
  else
    newNumXTRs = numXTRs - stopin + startin ;

//  No change in number of ranges: done
  if ( numXTRs == newNumXTRs ) {
    if ( straddle )
      tr[0] = T ;
    setListRange () ;
    return ;
  }

//
//  Make a new set of ranges
  XTimeRange* newXTR = new XTimeRange[newNumXTRs] ;

//
//    Extra range before
  if ( before ) {
    newXTR[0] = T ;
    for (i=0;i<numXTRs;i++)
      newXTR[i+1] = tr[i] ;
  }

//
//    Extra range after
  else if ( after ) {
    for (i=0;i<numXTRs;i++)
      newXTR[i] = tr[i] ;
    newXTR[numXTRs] = T ;
  }

//
//    Straddling range
  else if ( straddle )
    newXTR[0] = T ;

//
//    Extra range in between
  else if ( between ) {
    for (i=0;i<between;i++)
      newXTR[i] = tr[i] ;
    newXTR[between] = T ;
    for (i=between;i<numXTRs;i++)
      newXTR[i+1] = tr[i] ;
  }

//
//    Rearrange the ranges
  else {
//      Cover the new part in a single range
    tr[stopin].setStart (tr[startin].METStart()) ;
//      Now copy the remaining ones
    int j=0 ;
    for (i=0;i<startin;i++,j++)
      newXTR[j] = tr[i] ;
    for (i=stopin;i<numXTRs;i++,j++)
      newXTR[j] = tr[i] ;
  }

//
//  Exchange the two lists
  delete [] tr ;
  tr = newXTR ;
  numXTRs = newNumXTRs ;
  setListRange () ;

  return ;
}

//
//   -----------------------
// -- XTRList::setListRange --
//   -----------------------
//

// Description:
// Update the list range
void XTRList::setListRange (void) {
  int i, j, remove=0 ;

  if ( numXTRs )
    empty = 0 ;
  for (i=0; i<numXTRs; i++)
    if ( tr[i].isEmpty() )
      remove++ ;
  if ( remove ) {
    if ( remove >= numXTRs ) {
      numXTRs = 0 ;
      empty = 1 ;
    }
    else {
      XTimeRange* newXTR = new XTimeRange[numXTRs - remove] ;
      for (i=0, j=0; i<numXTRs; i++)
	if ( !tr[i].isEmpty() )
	  newXTR[j++] = tr[i] ;
      delete [] tr ;
      tr = newXTR ;
      numXTRs -= remove ;
      empty = 0 ;
    }
  }

  if ( !empty )
    listRange.resetRange (tr[0].METStart(), tr[numXTRs-1].METStop()) ;
  else
    listRange.resetRange (0.0, -1.0) ;
}
