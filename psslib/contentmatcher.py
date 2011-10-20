#-------------------------------------------------------------------------------
# pss: contentmatcher.py
#
# ContentMatcher class that matches the contents of a file according to a given
# pattern.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import re
import sys

from .matchresult import MatchResult


class ContentMatcher(object):
    def __init__(self,
            pattern,
            ignore_case=False,
            invert_match=False,
            whole_words=False,
            literal_pattern=False,
            max_match_count=sys.maxsize):
        """ Create a new ContentMatcher for matching the pattern in files.
            The parameters are the "matching rules".

            When created, the match_file method can be called multiple times
            for various files.

            pattern:
                The pattern (regular expression) to match, as a string

            ignore_case:
                If True, the pattern will ignore case when matching

            invert_match:
                Only non-matching lines will be returned. Note that in this 
                case 'matching_column_ranges' of the match results will be 
                empty

            whole_words:
                Force the pattern to match only whole words

            literal_pattern:
                Quote all special regex chars in the pattern - the pattern
                should match literally

            max_match_count:
                Maximal amount of matches to report for a search
        """
        self.regex = self._create_regex(pattern, 
                            ignore_case=ignore_case,
                            whole_words=whole_words,
                            literal_pattern=literal_pattern)
        self.invert_match = invert_match
        self.max_match_count = max_match_count
            
    def match_file(self, fileobj, max_match_count=sys.maxsize):
        """ Perform matching in the file according to the matching rules. Yield
            MatchResult objects.

            fileobj is a file-like object, being read from the beginning.
            max_match_count: can be set for each file individually.
        """
        nmatch = 0
        max_match_count = min(max_match_count, self.max_match_count)

        for lineno, line in enumerate(fileobj):
            lineno += 1 # file line-numbering is 1-based
            if not self.invert_match:
                col_ranges = []
                # Iterate over all matches of the pattern in the line,
                # noting each matching column range.
                for mo in self.regex.finditer(line):
                    col_ranges.append(mo.span())
                if len(col_ranges) > 0:
                    nmatch += 1
                    yield MatchResult(line, lineno, col_ranges)
            else:
                # invert match: only return lines that don't match the
                # pattern anywhere
                if not self.regex.search(line):
                    nmatch += 1
                    yield MatchResult(line, lineno, [])
            if nmatch >= max_match_count:
                break

    def _create_regex(self,
            pattern,
            ignore_case=False,
            whole_words=False,
            literal_pattern=False):
        """ Utility for creating the compiled regex from pattern and options.
        """
        if literal_pattern:
            pattern = re.escape(pattern)
        if whole_words:
            # zzz: does it always make sense to surround with \b like this?
            pattern = r'\b' + pattern + r'\b'
        regex = re.compile(pattern, re.I if ignore_case else 0)
        return regex


if __name__ == '__main__':
    pass

