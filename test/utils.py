#-------------------------------------------------------------------------------
# pss: test/utils.py
#
# Utilities for unit-testing of pss
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import os


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
            raise RuntimeError('no dir in path')
        path = head
    return os.path.join(*reversed(partial_path_elems))

