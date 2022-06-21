#-------------------------------------------------------------------------------
# pss: py3compat.py
#
# This used to be a compatibility layer between Python 2 and 3; now Python 2
# is no longer supported, so this is just a collection of a few utility
# functions that may be refactored away in the future.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import sys
PY3 = sys.version_info[0] == 3
assert PY3, '''\
Python 2 is no longer supported by pss; if you need to use Python 2,
please download an older pss version (such as version 1.43).
'''


# str2bytes -- converts a given string (which we know not to contain
# unicode chars) to bytes.
#
# bytes2str -- converts a bytes object to a string
#
# int2byte -- takes an integer in the 8-bit range and returns
# a single-character byte object in py3 / a single-character string
# in py2.
#
from io import StringIO
def str2bytes(s):
    return s.encode('latin1')
def int2byte(i):
    return bytes((i,))
def bytes2str(b):
    return b.decode('utf-8')


def tostring(b):
    """ Convert the given bytes or string object to string
    """
    if isinstance(b, bytes):
        return bytes2str(b)
    else:
        return b
