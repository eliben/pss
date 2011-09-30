#!/usr/bin/env python

from psslib.defaultpssoutputformatter import DefaultPssOutputFormatter
from psslib.matchresult import MatchResult
from psslib.contentmatcher import ContentMatcher
from psslib.driver import pss_run

from psslib.colorama import init
import sys


#df = DefaultPssOutputFormatter(show_column_of_first_match=True)
#df.start_matches_in_file("joe/toe.poy")
#df.found_filename('sdsdfsdfsdf')
#df.context_separator()
#df.context_line('here I come\n', 45 )
#df.matching_line(MatchResult('abc = 24 + def - yuas\n', 40, [(6, 8), (11, 14)]))


pss_run(sys.argv[2:], pattern=sys.argv[1],
        type_pattern='zb',
        )


#matcher = ContentMatcher(
        #pattern='cde',
        #ignore_case=False,
        #invert_match=False,
        #whole_words=False,
        #literal_pattern=False,
        #max_match_count=1)

#matches = list(matcher.match_file(fileobj=open('test/testdirs/testdir1/subdir1/zb.zzz')))
#print(matches)

