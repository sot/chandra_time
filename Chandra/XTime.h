//----------------------------------------------------------------------
//
//RCS: $Id: XTime.h,v 1.1 2007-04-11 21:04:01 aldcroft Exp $
// File Name   : XTime.h
// Subsystem   : XFF 
// Programmer  : Arnold Rots, SAO
// Description : XTime, XTimeRange, and XTRList classes
//
// Make manpage:
//  genman -h -e -t -oXTime.3 XTime.h
//  troff -man XTime.3 | /usr/lib/lp/postscript/dpost -n2 | lpr3dup
//
// .NAME    XTime - XTime, XTimeRange, and XTRList classes
// .LIBRARY Util
// .HEADER  Time transformations and manipulations
// .INCLUDE XTime.h
// .FILE    XTime.C
//
// .SECTION AUTHOR
//  Arnold Rots,
//  USRA/SAO,
//  <arots@head-cfa.harvard.edu>
//
// .SECTION DESCRIPTION
// XTime allows transformations between four time systems in six
// formats.  The time systems are MET, TT, TAI, and UTC.
// The formats:
// seconds, MJD, JD (all three: double or long+double),
// date string ("yyyy:ddd:hh:mm:ss.ss..."),
// calendar date string ("yyyyMondd at hh:mm:ss.ss..."),
// and FITS date/time string ("yyyy-mm-ddThh:mm:ss.ss...").
//
// The method getDate allows specifying the number of decimals.
// The time system-specific methods return integer seconds.
// A time correction term is optional.  MET is elapsed seconds
// since MJDref (default: 1998-01-01T00:00:00(TT)).  Note that if
// MJDref is specified explicitly, it will be assumed to be in
// the time system specified in the constructor or set call.
//
// XTimeRange is an aggregate of two XTime objects and an EMPTY
// indicator.  An XTimeRange is considered empty if either the
// start or stop MET is non-positive, or if the start time is
// later than the stop time.
//
// An XTRList is a list of XTimeRanges; it includes methods to
// perform logical AND and OR operations between XTRLists and
// between XTRLists and XTimeRanges.
//
// Note that all instances of XTime will have one private member
// that holds the date strings.  It is the user's responsibility
// to copy the string returned by any of the date string methods,
// since the next call will overwrite it.  Especially, avoid
// generating more than one date string for the same object in a
// single statement, such as:
//
// cout << "Time : " << t.TTDate() << " or " << t.TTCalDate() << endl ;
//
// Leap seconds are taken from tai-utc.dat.  If not available:
// Included leap seconds: 1972 through 1999 (leap seconds 10
// through 32).
//
// .VERSION $Revision: 1.1 $
//
//----------------------------------------------------------------------
//

#ifndef XTIME_H
#define XTIME_H
#include <time.h>


//
//   ---------
// -- XTime --
//   ---------
//

class XTime {

//*  Private attributes
 
  long   MJDint      ;               // Integer part of time
  double MJDfr       ;               // Fractional part of time
  double timeZero    ;               // Time correction term in d
  char   tdate[32]   ;               // Date string
  long   MJDrefint   ;               // MJDref (integer part)
  double MJDreffr    ;               // MJDref (fractional part)
  int    leapflag    ;               // Indicator whether we are in a leap second
  double myLeaps     ;               // Leap seconds at this time
  double refLeaps    ;               // Leap seconds at reference epoch

//*  Static attributes

  static const double MJD0        ;  // JD - MJD
  static const long   MJD1972     ;  // MJD at 1972
  static const double DAY2SEC     ;  // Seconds per day
  static const double SEC2DAY     ;  // Inverse seconds per day
  static const long   MJDREFint   ;  // MJD at 1998.0 (integer part)
  static const double MJDREFfr    ;  // MJD at 1998.0 (fractional part)
  static const double REFLEAPS    ;  // Leap seconds at default MJDREF (1998.0 TT)
  static const double TAI2TT      ;  // TT - TAI
  static int    NUMLEAPSECS       ;  // Number of leap seconds
  static long   LEAPSMJD[100]     ;  // Leap second dates
  static double LEAPSECS[100]     ;  // Leap seconds
  static time_t WALLCLOCK0        ;  // Wallclock time when leap seconds were read
  static int    NUMOBJECTS        ;  // Number of XTime objects instantiated

 public:

//*    Enumeration types

  enum TimeSys {MET, TT, UTC, TAI} ;
  enum TimeFormat {SECS, JD, MJD, DATE, CALDATE, FITS} ;

//*  Private methods

 private:

  const char* monDay (const char* date, TimeFormat tf) ;
  void setleaps (double dt=5000000.0) ;
  int setmyleaps (double *leapval, long mjdi, double mjdf) ;

//*  Public methods

 public:

//*    Constructors

  XTime (void) ;
  XTime (double tt) ;
  XTime (double tt, TimeSys ts, TimeFormat tf=SECS,
         long mjdi=0, double mjdf=0.0) ;
  XTime (long tti, double ttf, TimeSys ts=TT, TimeFormat tf=MJD,
         long mjdi=0, double mjdf=0.0) ;
  XTime (const char* date, TimeSys ts=UTC, TimeFormat tf=DATE,
         long mjdi=0, double mjdf=0.0) ;

//*    Destructor

  ~XTime (void) ;

//*    Set methods

  void setLeaps (double dt=5000000.0) ;
  void set (double tt, TimeSys ts=MET, TimeFormat tf=SECS,
            long mjdi=0, double mjdf=0.0) ;
  void set (long tti, double ttf, TimeSys ts=TT, TimeFormat tf=MJD,
            long mjdi=0, double mjdf=0.0) ;
  void set (const char* date, TimeSys ts=UTC, TimeFormat tf=DATE,
            long mjdi=0, double mjdf=0.0) ;
  void setTZero (double tz) ;

//*    Get methods

  double get (TimeSys ts=TT, TimeFormat tf=SECS) const ;
  double mjd (long *mjdi, double *mjdf, TimeSys ts=TT) const ;
  double getMET (void) const ;
  double getTT (void) const ;
  double getTAI (void) const ;
  double getUTC (void) const ;
  double getTZero (void) const ;
  const char* getDate (TimeSys ts=UTC, TimeFormat tf=DATE, int dec=0) ;
  const char* UTDate (void) ;
  const char* TTDate (void) ;
  const char* TAIDate (void) ;
  const char* UTCalDate (void) ;
  const char* TTCalDate (void) ;
  const char* TAICalDate (void) ;
  const char* UTFITS (void) ;
  const char* TTFITS (void) ;
  const char* TAIFITS (void) ;
  double UTmjd (void) const ;
  double TTmjd (void) const ;
  double TAImjd (void) const ;
  double UTmjd (long *mjdi, double *mjdf) const ;
  double TTmjd (long *mjdi, double *mjdf) const ;
  double TAImjd (long *mjdi, double *mjdf) const ;
  double UTjd (void) const ;
  double TTjd (void) const ;
  double TAIjd (void) const ;
  int numObjects (void) ;
  int leapSecs (const double** secs) const ;

} ;

// Description:
// Constructor: default constructor; set time to zero.
inline XTime::XTime (void)
  : MJDint (MJDREFint), MJDfr (MJDREFfr), timeZero (0.0),
    MJDrefint (MJDREFint), MJDreffr (MJDREFfr),
    refLeaps (REFLEAPS), myLeaps (REFLEAPS), leapflag (0)
{ setleaps() ; }

// Description:
// Constructor: create from MET seconds (tt).
inline XTime::XTime (double tt)
  : MJDint (MJDREFint), MJDfr (MJDREFfr+tt*SEC2DAY), timeZero (0.0),
    MJDrefint (MJDREFint), MJDreffr (MJDREFfr),
    refLeaps (REFLEAPS), leapflag (0)
{
  setleaps() ;
  leapflag = setmyleaps (&myLeaps, MJDint, MJDfr) ;
}

// Description:
// Constructor: create from seconds, MJD, or JD (tt); specified
// by ts and tf; allows specification of MJDREF (mjdi+mjdf).
// Default for ts is MET; default for tf is SECS; default for
// mjdi is 0 (i.e., default value); default for mjdf is 0.0.
inline XTime::XTime (double tt, TimeSys ts, TimeFormat tf,
		     long mjdi, double mjdf)
  : timeZero (0.0), MJDrefint (MJDREFint), MJDreffr (MJDREFfr),
    refLeaps (REFLEAPS), leapflag (0)
{
  setleaps() ;
  set (tt, ts, tf, mjdi, mjdf) ;
}

// Description:
// Constructor: most general constructor; create from seconds,
// MJD, or JD (tti+ttf); specified by ts and tf; allows
// specification of MJD reference (mjdi+mjdf).
// Default for ts is TT; default for tf is MJD; default for
// mjdi is 0 (i.e., default value); default for mjdf is 0.0.
inline XTime::XTime (long tti, double ttf, TimeSys ts, TimeFormat tf,
		     long mjdi, double mjdf)
  : timeZero (0.0), MJDrefint (MJDREFint), MJDreffr (MJDREFfr),
    refLeaps (REFLEAPS), leapflag (0)
{
  setleaps() ;
  set (tti, ttf, ts, tf, mjdi, mjdf) ;
}

// Description:
// Constructor: create from a date string; create from DATE,
// CALDATE, or FITSDATE (date); specified by ts and tf; allows
// specification of MJD reference (mjdi+mjdf).
// Default for ts is UTC, for tf is DATE; default for mjdi is 0
// (i.e., default value); default for mjdf is 0.0.
inline XTime::XTime (const char* date, TimeSys ts, TimeFormat tf,
		     long mjdi, double mjdf)
  : timeZero (0.0), leapflag (0), MJDrefint (MJDREFint), MJDreffr (MJDREFfr), refLeaps (31.0)
{
  setleaps() ;
  set (date, ts, tf, mjdi, mjdf) ;
}

// Description:
// Destructor: decrement object counter
inline XTime::~XTime (void) {
  NUMOBJECTS-- ;
}

// Description:
// Set the time correction term (in s)
inline void XTime::setTZero (double tz) {
  timeZero = tz * SEC2DAY ;
  leapflag = setmyleaps (&myLeaps, MJDint, MJDfr+timeZero) ;
}

// Description:
// Force refreshing leapseconds table (public method).
// Function to set leap second table
// If it was more than abs(dt) seconds since the
// leap seconds were read, the leap second table
// is refreshed; if dt > 0, only additional leap
// seconds are added; if dt < 0, all leap seconds
// are refreshed.  The default is dt=5000000 (about
// two months).
inline void XTime::setLeaps (double dt) {
  setleaps (dt) ;
  NUMOBJECTS-- ;
}

// Description:
// Return MET seconds
inline double XTime::getMET (void) const {
  return ((MJDint - MJDrefint) + (MJDfr - MJDreffr) + timeZero) * DAY2SEC ;
}

// Description:
// Return TT seconds since MJDref
inline double XTime::getTT (void) const {
  return getMET () ;
}

// Description:
// Return TAI seconds since MJDref
inline double XTime::getTAI (void) const {
  return getMET () ;
}

// Description:
// Return UTC seconds since MJDref
inline double XTime::getUTC (void) const {
  return ((MJDint - MJDrefint) + (MJDfr - MJDreffr) + timeZero) * DAY2SEC
          - myLeaps + refLeaps ;
}

// Description:
// Return time zero point correction
inline double XTime::getTZero (void) const {
  return timeZero * DAY2SEC ;
}

// Description:
// Return time as UTC date string (integer seconds)
inline const char* XTime::UTDate (void) {
  return ( getDate (UTC, DATE, 0) ) ;
}

// Description:
// Return time as TT date string (integer seconds)
inline const char* XTime::TTDate (void) {
  return ( getDate (TT, DATE, 0) ) ;
}

// Description:
// Return time as TAI date string (integer seconds)
inline const char* XTime::TAIDate (void) {
  return ( getDate (TAI, DATE, 0) ) ;
}

// Description:
// Return time as UTC calendar date string (integer seconds)
inline const char* XTime::UTCalDate (void) {
  return ( getDate (UTC, CALDATE, 0) ) ;
}

// Description:
// Return time as TT calendar date string (integer seconds)
inline const char* XTime::TTCalDate (void) {
  return ( getDate (TT, CALDATE, 0) ) ;
}

// Description:
// Return time as TAI calendar date string (integer seconds)
inline const char* XTime::TAICalDate (void) {
  return ( getDate (TAI, CALDATE, 0) ) ;
}

// Description:
// Return time as UTC FITS date string (integer seconds)
inline const char* XTime::UTFITS (void) {
  return ( getDate (UTC, FITS, 0) ) ;
}

// Description:
// Return time as TT FITS date string (integer seconds)
inline const char* XTime::TTFITS (void) {
  return ( getDate (TT, FITS, 0) ) ;
}

// Description:
// Return time as TAI FITS date string (integer seconds)
inline const char* XTime::TAIFITS (void) {
  return ( getDate (TAI, FITS, 0) ) ;
}

// Description:
// Return time as MJD(UTC)
inline double XTime::UTmjd (void) const {
  long mjdi ;
  double mjdf ;
  return ( UTmjd (&mjdi, &mjdf) ) ;
}

// Description:
// Return time as MJD(TT)
inline double XTime::TTmjd (void) const {
  return ( MJDint + MJDfr + timeZero ) ;
}

// Description:
// Return time as MJD(TAI)
inline double XTime::TAImjd (void) const {
  return ( TTmjd() - TAI2TT * SEC2DAY ) ;
}

// Description:
// Return time as MJD(TT) and fill the arguments
// with the integer and fractional parts.
inline double XTime::TTmjd (long *mjdi, double *mjdf) const {
  *mjdi = MJDint ;
  *mjdf = MJDfr ;
  return ( TTmjd() ) ;
}

// Description:
// Return time as MJD(TAI) and fill the arguments
// with the integer and fractional parts.
inline double XTime::TAImjd (long *mjdi, double *mjdf) const {
  *mjdi = MJDint ;
  *mjdf = MJDfr - TAI2TT * SEC2DAY ;
  return ( TAImjd() ) ;
}

// Description:
// Return time as JD(UTC)
inline double XTime::UTjd (void) const {
  return ( UTmjd() + MJD0 ) ;
}

// Description:
// Return time as JD(TT)
inline double XTime::TTjd (void) const {
  return ( TTmjd() + MJD0 ) ;
}

// Description:
// Return time as JD(TAI)
inline double XTime::TAIjd (void) const {
  return ( TAImjd() + MJD0 ) ;
}

// Description:
// Return number of existing XTime objects
inline int XTime::numObjects (void) {
  return NUMOBJECTS ;
}

// Description:
// Return number of leapsecond entries.
// Actual times are in array secs.
inline int XTime::leapSecs (const double** secs) const {
  *secs = LEAPSECS ;
  return NUMLEAPSECS ;
}

//
//   --------------
// -- XTimeRange --
//   --------------
//

class XTimeRange {

//*  Private attributes

  XTime start ;
  XTime stop ;
  int empty ;                    // Empty defined as:
                                   // start or stop <= 0.0, or start >= stop
                                   // start == stop > 0.0 is empty!

//*  Private method

  void setEmpty (void) ;

//*  Public methods

 public:

//*    Constructors

  XTimeRange (void) ;
  XTimeRange (const XTime &T1, const XTime &T2) ;
  XTimeRange (double t1, double t2) ;

//*    Set Methods

  void setStart (const XTime &T1) ;      // Set start as XTime object
  void setStop (const XTime &T2) ;       // Set stop as XTime object
  void resetRange (const XTime &T1, const XTime &T2) ;
  void setStart (double t1) ;              // Set start as MET seconds
  void setStop (double t2) ;               // Set stop as MET seconds
  void resetRange (double t1, double t2) ;

//*    Get methods

  XTime TStart (void) const ;            // Return start as XTime object
  XTime TStop (void) const ;             // Return stop as XTime object
  double METStart (void) const ;           // Return start in MET seconds
  double METStop (void) const ;            // Return stop in MET seconds
  const char* UTStartDate (void) ;         // Return start as UTC date string
  const char* UTStopDate (void) ;          // Return stop as UTC date string
  const char* TTStartDate (void) ;         // Return start as TT date string
  const char* TTStopDate (void) ;          // Return stop as TT date string
  int isInRange (const XTime &T) const ;
  int isInRange (double t) const ;
  double totalTime (void) const ;          // Return total seconds
  int isEmpty (void) const ;               // Empty range?
  void printRange (void) ;                 // A two-liner in UTC date format
  void printRangeCal (void) ;              // A two-liner in UTC calendar format

} ;

// Description:
// Empty constructor
inline XTimeRange::XTimeRange (void)
  : start (0.0), stop (0.0), empty (1) { }

// Description:
// Constructor using XTime objects
inline XTimeRange::XTimeRange (const XTime &T1, const XTime &T2) 
  : start (T1), stop (T2) {
  setEmpty () ;
}

// Description:
// Constructor using MET seconds
inline XTimeRange::XTimeRange (double t1, double t2)
  : start (t1), stop (t2) {
  setEmpty () ;
}

// Description:
// Set start as XTime object
inline void XTimeRange::setStart (const XTime &T1) {
  start = T1 ;
  setEmpty () ;
}

// Description:
// Set stop as XTime object
inline void XTimeRange::setStop (const XTime &T2) {
  stop = T2 ;
  setEmpty () ;
}

// Description:
// Reset range with XTime objects
inline void XTimeRange::resetRange (const XTime &T1, const XTime &T2) {
  start = T1 ;
  stop = T2 ;
  setEmpty () ;
}

// Description:
// Set start as MET seconds
inline void XTimeRange::setStart (double t1) {
  start.set (t1) ;
  setEmpty () ;
}

// Description:
// Set start as MET seconds
inline void XTimeRange::setStop (double t2) {
  stop.set (t2) ;
  setEmpty () ;
}

// Description:
// Reset range in MET seconds
inline void XTimeRange::resetRange (double t1, double t2) {
  start.set (t1) ;
  stop.set (t2) ;
  setEmpty () ;
}

// Description:
// Return start as XTime object
inline XTime XTimeRange::TStart (void) const {
  return start ;
}

// Description:
// Return start as XTime object
inline XTime XTimeRange::TStop (void) const {
  return stop ;
}

// Description:
// Return start in MET seconds
inline double XTimeRange::METStart (void) const {
  return start.getMET () ;
}

// Description:
// Return stop in MET seconds
inline double XTimeRange::METStop (void) const {
  return stop.getMET () ;
}

// Description:
// Return start as UTC date string
inline const char* XTimeRange::UTStartDate (void) {
  return start.UTDate () ;
}

// Description:
// Return stop as UTC date string
inline const char* XTimeRange::UTStopDate (void) {
  return stop.UTDate () ;
}

// Description:
// Return start as TT date string
inline const char* XTimeRange::TTStartDate (void) {
  return start.TTDate () ;
}

// Description:
// Return stop as TT date string
inline const char* XTimeRange::TTStopDate (void) {
  return stop.TTDate () ;
}

// Description:
// Return -1 if before, 0 if in range, 1 if after
inline int XTimeRange::isInRange (double t) const {
  if ( t < start.getMET() )
    return -1 ;
  else if ( t > stop.getMET() )
    return 1 ;
  else if ( empty )
    return 1 ;
  else
    return 0 ;
}

// Description:
// Return -1 if before, 0 if in range, 1 if after
inline int XTimeRange::isInRange (const XTime &T) const {
  return isInRange (T.getMET()) ;
}

// Description:
// Return total seconds
inline double XTimeRange::totalTime (void) const {
  return ( empty ? 0.0 : ( stop.getMET() - start.getMET() ) ) ;
}

// Description:
// Empty range?
inline int XTimeRange::isEmpty (void) const {
  return empty ;
}

//
//   ---------
// -- XTRList --
//   ---------
//

class XTRList {

//*  Private attributes

  XTimeRange listRange ;
  int numXTRs ;
  XTimeRange* tr ;
  int empty ;

//*  Public methods

 public:

//*    Constructors

  XTRList (void) ;
  XTRList (const XTimeRange &T) ;
  XTRList (const XTRList &trl) ;
  XTRList (const XTRList &trl1, const XTRList &trl2) ;

//*    Destructor

  ~XTRList () ;

//*    Operators

  XTRList& operator=(const XTRList &trl) ;

//*    Processing (modification) methods

  void orList (const XTRList &trl) ;
  void notList (const XTimeRange &T) ;
  void andRange (const XTimeRange &T) ;
  void orRange (const XTimeRange &T) ;

//*    Get methods

  int isInRange (const XTime &T) const ;         //  Return 0 if in range
  int isInRange (double t) const ;
  int getNumXTRs (void) const ;
  const XTimeRange* getRange (int i) const ;
  const XTimeRange* getRange (const XTime &T) const ;
  const XTimeRange* getRange (double t) const ;
  void setListRange (void) ;
  int isEmpty (void) const ;
  double totalTime (void) const ;
  void printList (void) ;
  void printListCal (void) ;
} ;

// Description:
// Default constructor for a single XTimeRange List
inline XTRList::XTRList (void)
  : empty(1), numXTRs (1) {
  tr = new XTimeRange () ;
  listRange =* tr ;
}

// Description:
// Constructor for a single XTimeRange List
inline XTRList::XTRList (const XTimeRange &T)
  : listRange (T), numXTRs (1) {
  tr = new XTimeRange (T) ;
  empty = T.isEmpty () ;
}

// Description:
// Destructor
inline XTRList::~XTRList () {
  delete [] tr ;
}

// Description:
// Return number of ranges in list
inline int XTRList::getNumXTRs (void) const {
  return numXTRs ;
}

// Description:
// Return range no. ,i>
inline const XTimeRange* XTRList::getRange (int i) const {
  if ( ( i >= 0 ) && ( i < numXTRs ) )
    return tr+i ;
  else
    return NULL ;
}

// Description:
// Empty list?
inline int XTRList::isEmpty (void) const {
  return empty ;
}

#endif             // XTIME_H
