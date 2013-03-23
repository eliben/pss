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

from .py3compat import tostring
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
                The pattern (regular expression) to match, as a string or bytes
                object (should match the stream passed to the match method).

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
        if invert_match:
            self.match_file = self.inverted_matcher
        else:
            self.match_file = self.matcher
        self.max_match_count = max_match_count

        # Cache frequently used attributes for faster access
        self._finditer = self.regex.finditer
        self._search = self.regex.search

        # Optimize a common case: searching for a simple non-regex string.
        # In this case, we don't need regex matching - using str.find is
        # faster.
        self._findstr = None
        if (    not ignore_case and not whole_words and
                self._pattern_is_simple(pattern)):
            self._findstr = pattern
            self._findstrlen = len(self._findstr)

    def matcher(self, fileobj, max_match_count=sys.maxsize):
        """ Perform matching in the file according to the matching rules. Yield
            MatchResult objects.

            fileobj is a file-like object, being read from the beginning.
            max_match_count: can be set for each file individually.
        """
        nmatch = 0
        max_match_count = min(max_match_count, self.max_match_count)
        for lineno, line in enumerate(fileobj, 1):
            # Iterate over all matches of the pattern in the line,
            # noting each matching column range.
            if self._findstr:
                # Make the common case faster: there's no match in this line, so
                # bail out ASAP.
                i = line.find(self._findstr, 0)
                if i == -1:
                    continue
                col_ranges = []
                while i >= 0:
                    startnext = i + self._findstrlen
                    col_ranges.append((i, startnext))
                    i = line.find(self._findstr, startnext)
            else:
                col_ranges = [mo.span() for mo in self._finditer(line) if mo]
            if col_ranges:
                yield MatchResult(line, lineno, col_ranges)
                nmatch += 1
                if nmatch >= max_match_count:
                    break

    def inverted_matcher(self, fileobj, max_match_count=sys.maxsize):
        """ Perform inverted matching in the file according to the matching
            rules. Yield MatchResult objects.

            fileobj is a file-like object, being read from the beginning.
            max_match_count: can be set for each file individually.
        """
        nmatch = 0
        max_match_count = min(max_match_count, self.max_match_count)
        for lineno, line in enumerate(fileobj, 1):
            # Invert match: only return lines that don't match the
            # pattern anywhere
            if not self._search(line):
                yield MatchResult(line, lineno, [])
                nmatch += 1
                if nmatch >= max_match_count:
                    break

    def _pattern_is_simple(self, pattern):
        """ A "simple" pattern that can be matched with str.find and doesn't
            require a regex engine.
        """
        return bool(re.match('[\w_]+$', tostring(pattern)))

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
            b = r'\b' if isinstance(pattern, str) else br'\b'
            pattern = b + pattern + b
        regex = re.compile(pattern, re.I if ignore_case else 0)
        return regex


if __name__ == '__main__':
    pass

