#-------------------------------------------------------------------------------
# pss: py3compat.py
#
# Some Python2&3 compatibility code
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import sys
PY3 = sys.version_info[0] == 3


identity_func = lambda x: x

# str2bytes -- converts a given string (which we know not to contain 
# unicode chars) to bytes.
#
# bytes2str -- converts a bytes object to a string
#
# int2byte -- takes an integer in the 8-bit range and returns
# a single-character byte object in py3 / a single-character string
# in py2.
#
if PY3:
    def str2bytes(s):
        return s.encode('latin1')
    def int2byte(i):
        return bytes((i,))
    def bytes2str(b):
        return b.decode('utf-8')
else:
    str2bytes = identity_func
    int2byte = chr
    bytes2str = identity_func


def tostring(b):
    """ Convert the given bytes or string object to string
    """
    if isinstance(b, bytes):
        return bytes2str(b)
    else:
        return b

