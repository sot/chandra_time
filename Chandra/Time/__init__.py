# Licensed under a 3-clause BSD style license - see LICENSE.rst
from .Time import *

__version__ = '3.20.3'


def test(*args, **kwargs):
    '''
    Run py.test unit tests.
    '''
    import testr
    return testr.test(*args, **kwargs)
