try:
    from cStringIO import StringIO
except ImportError:
    # python 3
    from io import StringIO

import os
import pprint
import sys
import unittest

sys.path.extend(['.', '..'])
from psslib.contentmatcher import ContentMatcher, MatchResult


text1 = r'''some line vector<int>
another line here
this has line and then 'line' again
and here we have none vector <int>
Uppercase Line yes?
         line start
many lines and linen too! even a spline yess
'''

text2 = r'''creampie
apple pie and plum pie
pierre is $\t jkm
dptr .*n and again some pie
'''


class TestContentMatcher(unittest.TestCase):
    def num_matches(self, pattern, text, **kwargs):
        """ Number of matching lines for the pattern in the text. kwargs are
            passed to ContentMatcher.
        """
        cm = ContentMatcher(pattern, **kwargs)
        return len(list(cm.match_file(StringIO(text))))

    def assertMatches(self, cm, text, exp_matches):
        # exp_matches is a list of pairs: lineno, list of column ranges
        matches = list(cm.match_file(StringIO(text)))
        self.assertEqual(len(matches), len(exp_matches))
        textlines = text.split('\n')
        for n, exp_match in enumerate(exp_matches):
            exp_matchresult = MatchResult(
                    textlines[exp_match[0] - 1] + '\n',
                    exp_match[0],
                    exp_match[1])
            self.assertEqual(exp_matchresult, matches[n])

    def test_defaults(self):
        cm = ContentMatcher('line')
        self.assertMatches(cm, text1, [
                (1, [(5, 9)]),
                (2, [(8, 12)]),
                (3, [(9, 13), (24, 28)]),
                (6, [(9, 13)]),
                (7, [(5, 9), (15, 19), (35, 39)])])

        cm = ContentMatcher('Line')
        self.assertMatches(cm, text1, [(5, [(10, 14)])])

        cm = ContentMatcher('L[ix]ne')
        self.assertMatches(cm, text1, [(5, [(10, 14)])])

        cm = ContentMatcher('upper')
        self.assertMatches(cm, text1, [])

    def test_regex_match(self):
        # literal "yes?" matches once
        self.assertEqual(self.num_matches(r'yes\?', text1), 1)
        # regex matching ye(s|) - twice
        self.assertEqual(self.num_matches(r'yes?', text1), 2)

        self.assertEqual(self.num_matches(r'vector', text1), 2)
        self.assertEqual(self.num_matches(r'vector *<', text1), 2)
        self.assertEqual(self.num_matches(r'vector +<', text1), 1)

    def test_id_regex_match_detailed(self):
        t1 = 'some line with id_4 and vec8f too'
        self.assertEqual(self.num_matches(r'id_4', t1), 1)
        self.assertEqual(self.num_matches(r'8f', t1), 1)
        self.assertEqual(self.num_matches(r'[0-9]f', t1), 1)

        self.assertEqual(self.num_matches('8F', t1, ignore_case=True), 1)
        self.assertEqual(self.num_matches('84', t1, ignore_case=True), 0)
        self.assertEqual(self.num_matches('84', t1, invert_match=True), 1)

    def test_ignore_case(self):
        cm = ContentMatcher('upper', ignore_case=True)
        self.assertMatches(cm, text1, [(5, [(0, 5)])])

    def test_invert_match(self):
        cm = ContentMatcher('line', invert_match=True)
        self.assertMatches(cm, text1, [(4, []), (5, [])])

        cm = ContentMatcher('line', invert_match=True, ignore_case=True)
        self.assertMatches(cm, text1, [(4, [])])

    def test_max_count(self):
        cm = ContentMatcher('line', max_match_count=1)
        self.assertMatches(cm, text1, [(1, [(5, 9)])])

        cm = ContentMatcher('line', max_match_count=2)
        self.assertMatches(cm, text1,
                [(1, [(5, 9)]), (2, [(8, 12)])])

        cm = ContentMatcher('a', max_match_count=1)
        self.assertMatches(cm, text1,
                [(2, [(0, 1)])])

    def test_whole_words(self):
        cm = ContentMatcher('pie', whole_words=True)
        self.assertMatches(cm, text2, [
                (2, [(6, 9), (19, 22)]),
                (4, [(24, 27)])])

        cm = ContentMatcher('.*n', literal_pattern=True)
        self.assertMatches(cm, text2, [(4, [(5, 8)])])

        cm = ContentMatcher(r'$\t', literal_pattern=True)
        self.assertMatches(cm, text2, [(3, [(10, 13)])])

        cm = ContentMatcher(r'$\t', literal_pattern=False)
        self.assertMatches(cm, text2, [])


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
