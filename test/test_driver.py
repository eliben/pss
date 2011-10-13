import os, sys
import unittest

sys.path.insert(0, '.')
sys.path.insert(0, '..')
from psslib.driver import pss_run
from psslib.outputformatter import OutputFormatter
from test.utils import path_to_testdir, path_relative_to_dir


class MockOutputFormatter(OutputFormatter):
    """ A mock output formatter to be used in tests. Stores all output emitted
        to it in a list of pairs (output_type, data)
    """
    def __init__(self, basepath):
        self.basepath = basepath
        self.output = []
        
    def start_matches_in_file(self, filename):
        relpath = path_relative_to_dir(filename, self.basepath)
        self.output.append(
            ('START_MATCHES', os.path.normpath(relpath)))

    def end_matches_in_file(self, filename):
        relpath = path_relative_to_dir(filename, self.basepath)
        self.output.append(
            ('END_MATCHES', os.path.normpath(relpath)))
        
    def matching_line(self, matchresult):
        self.output.append(('MATCH',
            (matchresult.matching_lineno, matchresult.matching_column_ranges)))

    def context_line(self, line, lineno):
        self.output.append(('CONTEXT', lineno))

    def context_separator(self):
        self.output.append(('CONTEXT_SEP', None))

    def binary_file_matches(self, msg):
        self.output.append(('BINARY_MATCH', msg))

    def found_filename(self, filename):
        relpath = path_relative_to_dir(filename, self.basepath)
        self.output.append((
            'FOUND_FILENAME', os.path.normpath(relpath)))


class TestDriver(unittest.TestCase):
    testdir1 = path_to_testdir('testdir1')

    def setUp(self):
        self.of = MockOutputFormatter('testdir1')

    def test_basic(self):
        pss_run(
            roots=[self.testdir1],
            pattern='abc',
            output_formatter=self.of,
            include_types=['cc'])

        self.assertEqual(self.of.output,
                self._gen_outputs_in_file(
                    'testdir1/filea.c', [('MATCH', (2, [(4, 7)]))]) +
                self._gen_outputs_in_file(
                    'testdir1/filea.h', [('MATCH', (1, [(8, 11)]))]))

    def test_two_matches(self):
        pss_run(
            roots=[self.testdir1],
            pattern='abc',
            output_formatter=self.of,
            include_types=['ada'])

        self.assertEqual(self.of.output,
                self._gen_outputs_in_file(
                    'testdir1/subdir1/someada.adb',
                    [   ('MATCH', (4, [(18, 21)])),
                        ('MATCH', (14, [(15, 18)]))]))

    def test_context_separate(self):
        # context set to +/-3, so it's not "merged" between the two matches
        # and stays separate, with a context separator
        pss_run(
            roots=[self.testdir1],
            pattern='abc',
            output_formatter=self.of,
            ncontext_before=3,
            ncontext_after=3,
            include_types=['ada'])
        
        self.assertEqual(self.of.output,
                self._gen_outputs_in_file(
                    'testdir1/subdir1/someada.adb',
                    [   ('CONTEXT', 1), ('CONTEXT', 2), ('CONTEXT', 3),
                        ('MATCH', (4, [(18, 21)])),
                        ('CONTEXT', 5), ('CONTEXT', 6), ('CONTEXT', 7),
                        ('CONTEXT_SEP', None),
                        ('CONTEXT', 11), ('CONTEXT', 12), ('CONTEXT', 13),
                        ('MATCH', (14, [(15, 18)])),
                        ('CONTEXT', 15), ('CONTEXT', 16), ('CONTEXT', 17), 
                        ]))

    def test_context_merged(self):
        # context set to +/-6, so it's merged between matches
        pss_run(
            roots=[self.testdir1],
            pattern='abc',
            output_formatter=self.of,
            ncontext_before=6,
            ncontext_after=6,
            include_types=['ada'])
        
        self.assertEqual(self.of.output,
                self._gen_outputs_in_file(
                    'testdir1/subdir1/someada.adb',
                    [   ('CONTEXT', 1), ('CONTEXT', 2), ('CONTEXT', 3),
                        ('MATCH', (4, [(18, 21)])),
                        ('CONTEXT', 5), ('CONTEXT', 6), ('CONTEXT', 7),
                        ('CONTEXT', 8), ('CONTEXT', 9), ('CONTEXT', 10),
                        ('CONTEXT', 11), ('CONTEXT', 12), ('CONTEXT', 13),
                        ('MATCH', (14, [(15, 18)])),
                        ('CONTEXT', 15), ('CONTEXT', 16), ('CONTEXT', 17), 
                        ('CONTEXT', 18), ('CONTEXT', 19), ('CONTEXT', 20),
                        ]))

    def test_ignored_dirs(self):
        rootdir = path_to_testdir('ignored_dirs')

        # no dirs ignored
        of = MockOutputFormatter('ignored_dirs')
        pss_run(
            roots=[rootdir],
            output_formatter=of,
            pattern='def',
            include_types=['xml'])

        # Comparing as sorted because on different systems the files
        # returned in a different order
        #
        self.assertEqual(sorted(of.output),
                sorted(self._gen_outputs_in_file(
                    'ignored_dirs/file.xml', [('MATCH', (1, [(3, 6)]))]) +
                self._gen_outputs_in_file(
                    'ignored_dirs/dir1/file.xml', [('MATCH', (1, [(3, 6)]))]) +
                self._gen_outputs_in_file(
                    'ignored_dirs/dir2/file.xml', [('MATCH', (1, [(3, 6)]))])))

        # both dir1 and dir2 ignored
        of = MockOutputFormatter('ignored_dirs')
        pss_run(
            roots=[rootdir],
            output_formatter=of,
            pattern='def',
            add_ignored_dirs=['dir1', 'dir2'],
            include_types=['xml'])

        self.assertEqual(of.output,
                self._gen_outputs_in_file(
                    'ignored_dirs/file.xml', [('MATCH', (1, [(3, 6)]))]))

        # dir1 ignored (dir2 also appears in remove_ignored_dirs)
        of = MockOutputFormatter('ignored_dirs')
        pss_run(
            roots=[rootdir],
            output_formatter=of,
            add_ignored_dirs=['dir1', 'dir2'],
            remove_ignored_dirs=['dir2'],
            pattern='def',
            include_types=['xml'])

        self.assertEqual(sorted(of.output),
                sorted(self._gen_outputs_in_file(
                    'ignored_dirs/file.xml', [('MATCH', (1, [(3, 6)]))]) +
                self._gen_outputs_in_file(
                    'ignored_dirs/dir2/file.xml', [('MATCH', (1, [(3, 6)]))])))

    def test_only_find_files(self):
        pss_run(
            roots=[self.testdir1],
            pattern='abc',
            output_formatter=self.of,
            include_types=['cc'],
            only_find_files=True)

        def _build_found_list(filenames):
            return sorted(
                ('FOUND_FILENAME', os.path.normpath(f)) for f in filenames)

        self.assertEqual(sorted(self.of.output),
            _build_found_list([
                'testdir1/filea.c', 'testdir1/filea.h',
                'testdir1/subdir1/filey.c', 'testdir1/subdir1/filez.c']))

        # now with a pattern
        self.setUp()
        pss_run(
            roots=[self.testdir1],
            pattern='abc',
            output_formatter=self.of,
            type_pattern='.*y\.',
            include_types=['cc'],
            only_find_files=True)

        self.assertEqual(self.of.output,
            _build_found_list(['testdir1/subdir1/filey.c']))

    def test_binary_matches(self):
        pss_run(
            roots=[self.testdir1],
            pattern='cde',
            output_formatter=self.of,
            type_pattern='zb')
        
        binary_match = self.of.output[-1]
        self.assertEqual(binary_match[0], 'BINARY_MATCH')
        self.assertTrue(binary_match[1].find('zb.zzz') > 0)

    def test_include_types(self):
        rootdir = path_to_testdir('test_types')
        def outputs(filename):
            return self._gen_outputs_in_file(
                        filename, 
                        [('MATCH', (1, [(0, 3)]))])

        # include only js and java
        of = MockOutputFormatter('test_types')
        pss_run(
            roots=[rootdir],
            output_formatter=of,
            pattern='abc',
            include_types=['js', 'java'])

        self.assertEqual(sorted(of.output), sorted(
                outputs('test_types/a.java') + 
                outputs('test_types/a.js')))

        # empty include_types - so include all known types
        of = MockOutputFormatter('test_types')
        pss_run(
            roots=[rootdir],
            output_formatter=of,
            pattern='abc',
            include_types=[])

        self.assertEqual(sorted(of.output), sorted(
                outputs('test_types/a.java') + 
                outputs('test_types/a.js') +
                outputs('test_types/a.lua') +
                outputs('test_types/a.cmd') +
                outputs('test_types/a.bat')))

        # empty include_types, but some are excluded
        of = MockOutputFormatter('test_types')
        pss_run(
            roots=[rootdir],
            output_formatter=of,
            pattern='abc',
            exclude_types=['batch', 'js', 'java'],
            include_types=[])

        self.assertEqual(sorted(of.output), sorted(
                outputs('test_types/a.lua')))

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
