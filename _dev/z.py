#!/usr/bin/env python

import sys

from psslib.defaultpssoutputformatter import DefaultPssOutputFormatter
from psslib.matchresult import MatchResult
from psslib.contentmatcher import ContentMatcher
from psslib.driver import pss_run
from psslib.utils import istextfile

with open('psslib/__pycache__/outputformatter.cpython-33.pyc', 'rb') as f:
    print istextfile(f)
    f.seek(0)

    cm = ContentMatcher('imp')
    matches = cm.match_file(f)
    print(list(matches))

