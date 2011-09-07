#-------------------------------------------------------------------------------
# pss: matchresult.py
#
# MatchResult - represents a single match result from a file.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
from collections import namedtuple


# matching_line:
#   The line that matched the pattern
#
# matching_lineno:
#   Line number of the matching line
#
# matching_column_ranges:
#   A list of pairs. Its length is the amount of matches for the pattern in the
#   line. Each pair of column numbers specifies the exact range in the line
#   that matched the pattern. The range is right-open like all ranges in
#   Python.
#   I.e. range (2, 5) means columns 2,3,4 matched
#
MatchResult = namedtuple('MatchResult', ' '.join([
                'matching_line',
                'matching_lineno',
                'matching_column_ranges']))

