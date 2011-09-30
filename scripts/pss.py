#!/usr/bin/env python
#-------------------------------------------------------------------------------
# pss: pss.py
#
# Top-level script
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import os, sys
from optparse import OptionParser

# Make sure we can import psslib, even if run from the source distribution
# root or its scripts/ dir
try:
    import psslib
except ImportError:
    sys.path.extend(['.', '..')

from psslib import __version
from psslib.driver import pss_run


def main():
    # parse the command-line arguments and invoke pss_run


if __name__ == '__main__':
    main()

