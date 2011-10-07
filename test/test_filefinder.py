import os
import sys
import unittest

sys.path.insert(0, '.')
sys.path.insert(0, '..')
from psslib.filefinder import FileFinder
from test.utils import path_to_testdir, path_relative_to_dir


class TestFileFinder(unittest.TestCase):
    testdir_simple = path_to_testdir('simple_filefinder')

    all_c_files = [
            'simple_filefinder/.bzr/hgc.c',
            'simple_filefinder/a.c',
            'simple_filefinder/anothersubdir/a.c',
            'simple_filefinder/c.c']
    
    all_cpp_files = [
            'simple_filefinder/.bzr/ttc.cpp',
            'simple_filefinder/anothersubdir/CVS/r.cpp',
            'simple_filefinder/anothersubdir/deep/t.cpp',
            'simple_filefinder/anothersubdir/deep/tt.cpp',
            'simple_filefinder/b.cpp',
            'simple_filefinder/truesubdir/gc.cpp',
            'simple_filefinder/truesubdir/r.cpp']

    c_and_cpp_files = sorted(all_c_files + all_cpp_files)

    def _find_files(self, roots, **kwargs):
        """ Utility method for running FileFinder with the provided arguments.
            Return a sorted list of found files. The file names are processed
            to make path relative to the simple_filefinder dir.
        """
        ff = FileFinder(roots, **kwargs)
        return sorted(list(path_relative_to_dir(path, 'simple_filefinder')
                                for path in ff.files()))

    def assertPathsEqual(self, first, second):
        """ Compare lists of paths together, normalizing them for portability.
        """
        self.assertEqual(
                list(map(os.path.normpath, first)),
                list(map(os.path.normpath, second)))

    def test_extensions(self):
        # just the .c files
        self.assertPathsEqual(
                self._find_files(
                    [self.testdir_simple],
                    search_extensions=['.c']),
                self.all_c_files)

        # just the .cpp files
        self.assertPathsEqual(
                self._find_files(
                    [self.testdir_simple],
                    search_extensions=['.cpp']),
                self.all_cpp_files)

        # both .c and .cpp files
        self.assertPathsEqual(
                self._find_files(
                    [self.testdir_simple],
                    search_extensions=['.cpp', '.c']),
                self.c_and_cpp_files)

        # search both .c and .cpp, but ask to ignore .c
        self.assertPathsEqual(
                self._find_files(
                    [self.testdir_simple],
                    search_extensions=['.cpp', '.c'],
                    ignore_extensions=['.c']),
                self.all_cpp_files)

    def test_no_recurse(self):
        # .c files from root without recursing
        self.assertPathsEqual(
                self._find_files(
                    [self.testdir_simple],
                    recurse=False,
                    search_extensions=['.c']),
                [   'simple_filefinder/a.c',
                    'simple_filefinder/c.c'])

    def test_ignore_dirs(self):
        self.assertPathsEqual(
                self._find_files(
                    [self.testdir_simple],
                    search_extensions=['.c'],
                    ignore_dirs=['anothersubdir', '.bzr']),
                [   'simple_filefinder/a.c',
                    'simple_filefinder/c.c'])

    def test_file_patterns(self):
        # search ignoring .c and .cpp on purpose, to get a small amount of 
        # results
        self.assertPathsEqual(
                self._find_files(
                    [self.testdir_simple],
                    ignore_extensions=['.c', '.cpp'],
                    ignore_file_patterns=['~$']),
                ['simple_filefinder/#z.c#'])

        self.assertPathsEqual(
                self._find_files(
                    [self.testdir_simple],
                    ignore_extensions=['.c', '.cpp'],
                    ignore_file_patterns=['~$', '#.+#$']),
                [])

        # use search_file_patterns
        self.assertPathsEqual(
                self._find_files(
                    [self.testdir_simple],
                    search_file_patterns=['^t']),
                [   'simple_filefinder/.bzr/ttc.cpp',
                    'simple_filefinder/anothersubdir/deep/t.cpp',
                    'simple_filefinder/anothersubdir/deep/tt.cpp'])

        # use search_file_patterns and ignore_file_patterns together
        # exclude file names with at least 3 alphanumeric chars before
        # the dot
        self.assertPathsEqual(
                self._find_files(
                    [self.testdir_simple],
                    ignore_file_patterns=['\w{3}\.'],
                    search_file_patterns=['^t']),
                [   'simple_filefinder/anothersubdir/deep/t.cpp',
                    'simple_filefinder/anothersubdir/deep/tt.cpp'])


#------------------------------------------------------------------------------
if __name__ == '__main__':
    #print(path_to_testdir('simple_filefinder'))

    #print(path_relative_to_dir('a/b/c/d.c', 'g'))
    unittest.main()


