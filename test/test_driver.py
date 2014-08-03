import os, sys
import unittest

sys.path.insert(0, '.')
sys.path.insert(0, '..')
from psslib.driver import pss_run
from test.utils import path_to_testdir, MockOutputFormatter


class TestDriver(unittest.TestCase):
    # Just basic sanity tests for pss_run
    # Do all the heavy testing in test_pssmain.py, because it also testse the
    # cmdline argument parsing and combination logic.
    #
    testdir1 = path_to_testdir('testdir1')

    def setUp(self):
        self.of = MockOutputFormatter('testdir1')

    def test_basic(self):
        match_found = pss_run(
            roots=[self.testdir1],
            pattern='abc',
            output_formatter=self.of,
            include_types=['cc'])

        self.assertEqual(sorted(self.of.output),
                sorted(self._gen_outputs_in_file(
                    'testdir1/filea.c', [('MATCH', (2, [(4, 7)]))]) +
                self._gen_outputs_in_file(
                    'testdir1/filea.h', [('MATCH', (1, [(8, 11)]))])))

        self.assertEquals(match_found, True)

    def _gen_outputs_in_file(self, filename, outputs):
        """ Helper method for constructing a list of output pairs in the format
            of MockOutputFormatter, delimited from both ends with START_MATCHES
            and END_MATCHES for the given filename.
        """
        seq = []
        seq.append(('START_MATCHES', os.path.normpath(filename)))
        seq.extend(outputs)
        seq.append(('END_MATCHES', os.path.normpath(filename)))
        return seq


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
