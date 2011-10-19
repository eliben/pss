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


# str2bytes -- converts a given string to bytes
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
else:
    str2bytes = lambda x: x
    int2byte = chr
