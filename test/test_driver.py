import os, sys
import unittest

sys.path.insert(0, '.')
sys.path.insert(0, '..')
from psslib.driver import pss_run
from test.utils import path_to_testdir, MockOutputFormatter


def matches(filename, outputs):
    """ Helper function for constructing a list of output pairs in the format
        of MockOutputFormatter, delimited from both ends with START_MATCHES
        and END_MATCHES for the given filename.
    """
    seq = []
    seq.append(('START_MATCHES', os.path.normpath(filename)))
    seq.extend(outputs)
    seq.append(('END_MATCHES', os.path.normpath(filename)))
    return seq


class TestDriver(unittest.TestCase):
    # Just basic sanity tests for pss_run
    # Do all the heavy testing in test_pssmain.py, because it also tests the
    # cmdline argument parsing and combination logic.
    testdir1 = path_to_testdir('testdir1')
    testdir4 = path_to_testdir('testdir4')

    def setUp(self):
        self.of1 = MockOutputFormatter('testdir1')
        self.of4 = MockOutputFormatter('testdir4')

    def test_basic(self):
        match_found = pss_run(
            roots=[self.testdir1],
            pattern='abc',
            output_formatter=self.of1,
            include_types=['cc'])

        self.assertEqual(
            sorted(self.of1.output),
            sorted(
                matches('testdir1/filea.c', [('MATCH', (2, [(4, 7)]))]) +
                matches('testdir1/filea.h', [('MATCH', (1, [(8, 11)]))])
            ))

        self.assertEquals(match_found, True)

    def test_only_find_files_with_include_types(self):
        match_found = pss_run(
            roots=[self.testdir1],
            pattern='abc',
            output_formatter=self.of1,
            only_find_files=True,
            include_types=['cc'])

        self.assertFoundFiles(
            self.of1,
            [
            'testdir1/filea.c',
            'testdir1/filea.h',
            'testdir1/subdir1/filey.c',
            'testdir1/subdir1/filez.c',
            ]
        )

        self.assertEquals(match_found, True)

    def test_only_find_files_with_include_pattern(self):
        match_found = pss_run(
            roots=[self.testdir4],
            pattern='Test',
            output_formatter=self.of4,
            only_find_files=True,
            include_patterns=['file[12]'])

        self.assertFoundFiles(
            self.of4,
            [
            'testdir4/file1.py',
            'testdir4/file2.py',
            'testdir4/file1.txt',
            'testdir4/file2.txt',
            ]
        )

        self.assertEquals(match_found, True)

    def test_only_find_files_with_include_patterns(self):
        match_found = pss_run(
            roots=[self.testdir4],
            pattern='Test',
            output_formatter=self.of4,
            only_find_files=True,
            include_patterns=['file[12]', 'main\d.py'])

        self.assertFoundFiles(
            self.of4,
            [
            'testdir4/file1.py',
            'testdir4/file2.py',
            'testdir4/file1.txt',
            'testdir4/file2.txt',
            'testdir4/main1.py',
            'testdir4/main2.py',
            'testdir4/main3.py',
            ]
        )

        self.assertEquals(match_found, True)

    def test_find_in_files_with_include_patterns(self):
        match_found = pss_run(
            roots=[self.testdir4],
            pattern='Test',
            output_formatter=self.of4,
            only_find_files=False,
            include_patterns=['file[12]', 'main\d.py'])

        self.assertEqual(
            sorted(self.of4.output),
            sorted(
                matches('testdir4/file1.py' , [('MATCH', (1, [(0, 4)]))]) +
                matches('testdir4/file2.py' , [('MATCH', (1, [(0, 4)]))]) +
                matches('testdir4/file1.txt', [('MATCH', (1, [(0, 4)]))]) +
                matches('testdir4/file2.txt', [('MATCH', (1, [(0, 4)]))]) +
                matches('testdir4/main1.py' , [('MATCH', (1, [(0, 4)]))]) +
                matches('testdir4/main2.py' , [('MATCH', (1, [(0, 4)]))]) +
                matches('testdir4/main3.py' , [('MATCH', (1, [(0, 4)]))])
            ))

        self.assertEquals(match_found, True)

    def test_only_find_files_with_exclude_patterns(self):
        match_found = pss_run(
            roots=[self.testdir4],
            pattern='Test',
            output_formatter=self.of4,
            only_find_files=True,
            exclude_patterns=['file[12].txt', 'file3', 'main.*.py'])

        self.assertFoundFiles(
            self.of4,
            [
            'testdir4/file1.py',
            'testdir4/file2.py',
            'testdir4/main1.txt',
            'testdir4/main2.txt',
            'testdir4/main3.txt',
            ]
        )

        self.assertEquals(match_found, True)

    def test_find_in_files_with_exclude_patterns(self):
        match_found = pss_run(
            roots=[self.testdir4],
            pattern='Test',
            output_formatter=self.of4,
            only_find_files=False,
            exclude_patterns=['file[12].txt', 'file3', 'main.*.py'])

        self.assertEqual(
            sorted(self.of4.output),
            sorted(
                matches('testdir4/file1.py' , [('MATCH', (1, [(0, 4)]))]) +
                matches('testdir4/file2.py' , [('MATCH', (1, [(0, 4)]))]) +
                matches('testdir4/main1.txt', [('MATCH', (1, [(0, 4)]))]) +
                matches('testdir4/main2.txt', [('MATCH', (1, [(0, 4)]))]) +
                matches('testdir4/main3.txt', [('MATCH', (1, [(0, 4)]))])
            ))

        self.assertEquals(match_found, True)

    def assertFoundFiles(self, output_formatter, expected_list):
        self.assertEqual(sorted(output_formatter.output),
            sorted(('FOUND_FILENAME', f) for f in expected_list))


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
