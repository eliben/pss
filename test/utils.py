#-------------------------------------------------------------------------------
# pss: test/utils.py
#
# Utilities for unit-testing of pss
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import os
import platform

from psslib.outputformatter import OutputFormatter


def path_to_testdir(testdir_name):
    """ Given a name of a test directory, find its full path.
    """
    testdir_root = os.path.split(__file__)[0]
    return os.path.join(testdir_root, 'testdirs', testdir_name)


def path_relative_to_dir(path, dir):
    """ Given a path and some dir (that should be part of the path), return
        only the part of the path relative to the dir. For example:

        path_relative_to_dir('a/b/c/file.c', 'c') ==> 'c/file.c'

        Assume dir actually is part of path. Otherwise, raise RuntimeError
    """
    partial_path_elems = []
    while True:
        head, tail = os.path.split(path)
        partial_path_elems.append(tail)
        if tail == dir:
            break
        elif not head:
            print(path)
            print(dir)
            raise RuntimeError('no dir in path')
        path = head
    return os.path.join(*reversed(partial_path_elems))


def filter_out_path(path):
    """ Some paths have to be filtered out to successully compare to pss's
        output.
    """
    if 'file_bad_symlink' in path and platform.system() == 'Windows':
        return True
    return False


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

    def matching_line(self, matchresult, filename):
        self.output.append(('MATCH',
            (matchresult.matching_lineno, matchresult.matching_column_ranges)))

    def context_line(self, line, lineno, filename):
        self.output.append(('CONTEXT', lineno))

    def context_separator(self):
        self.output.append(('CONTEXT_SEP', None))

    def binary_file_matches(self, msg):
        self.output.append(('BINARY_MATCH', msg))

    def found_filename(self, filename):
        relpath = path_relative_to_dir(filename, self.basepath)
        self.output.append((
            'FOUND_FILENAME', os.path.normpath(relpath)))
