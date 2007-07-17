%module axTime3
%include "typemaps.i"

%{
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <iostream.h>
#include <fstream.h>
#include <iomanip.h>
#include <limits.h>
#include "XTime.h"

char *convert_time(char *,char *,char *,char *,char *);
%}

%newobject convert_time;

extern char *convert_time(char *time_in,
      	                   char *ts_in,
	                   char *tf_in,
	                   char *ts_out,
	                   char *tf_out
                  	  );
