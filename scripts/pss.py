#!/usr/bin/env python

# top-level script

try:
    from psslib import pssmain
except ImportError:
    import sys
    sys.path.append('..')
    from psslib import pssmain


if __name__ == '__main__':
    pssmain()


