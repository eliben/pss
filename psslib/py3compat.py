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
