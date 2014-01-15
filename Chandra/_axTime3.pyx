# distutils: language = c++
# distutils: sources = Chandra/axTime3.cc Chandra/XTime.cc

from six import PY3

cdef extern from "axTime3.h":
    void *_convert_time(char *time_in,
                        char *ts_in,
                        char *tf_in,
                        char *ts_out,
                        char *tf_out,
                        char *time_out,)

def convert_time(time_in, ts_in, tf_in, ts_out, tf_out):
    time_out = " " * 80
    if PY3:
        time_in = bytes(time_in, encoding='ascii')
        ts_in = bytes(ts_in, encoding='ascii')
        tf_in = bytes(tf_in, encoding='ascii')
        ts_out = bytes(ts_out, encoding='ascii')
        tf_out = bytes(tf_out, encoding='ascii')
        time_out = bytes(time_out, encoding='ascii')
    _convert_time(time_in, ts_in, tf_in, ts_out, tf_out, time_out)
    if PY3:
        time_out = time_out.decode('ascii')
    length = time_out.index('\x00')
    return time_out[:length]
