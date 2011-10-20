#-------------------------------------------------------------------------------
# pss: filefinder.py
#
# FileFinder class that finds files recursively according to various rules.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import os
import re


class FileFinder(object):
    def __init__(self,
            roots,
            recurse=True,
            ignore_dirs=[],
            search_extensions=[],
            ignore_extensions=[],
            search_file_patterns=[],
            ignore_file_patterns=[]):
        """ Create a new FileFinder. The parameters are the "search rules"
            that dictate which files are found.

            roots: 
                Root files/directories from which the search will start

            recurse:
                Should I recurse into sub-directories?

            ignore_dirs:
                Iterable of directory names that will be ignored during the
                search

            search_extensions:
                If non-empty, only files with extensions listed here will be
                found. If empty, files with all extensions will be found

            ignore_extensions:
                Files with extensions listed here will never be found.
                Overrides "search_*" rules

            search_file_patterns:
                If non-empty, only files with names matching these pattens will
                be found. If empty, no pattern restriction is applied

            ignore_file_patterns:
                Files with names matching these patterns will never be found.
                Overrides "search_*" rules
        """
        # Prepare internal data structures from the parameters
        self.roots = roots
        self.recurse = recurse
        self.search_extensions = set(search_extensions)
        self.ignore_extensions = set(ignore_extensions)
        self.ignore_dirs = set(ignore_dirs)
        self.search_file_patterns = [re.compile(p) for p in search_file_patterns]
        self.ignore_file_patterns = [re.compile(p) for p in ignore_file_patterns]

    def files(self):
        """ Generate files according to the search rules. Yield
            paths to files one by one.
        """
        for root in self.roots:
            if os.path.isfile(root):
                if self._file_is_found(root):
                    yield root
            else: # dir
                for dirpath, subdirs, files in os.walk(root):
                    prefix, dirname = os.path.split(dirpath)
                    if dirname in self.ignore_dirs:
                        # This dir should be ignored, so remove all its subdirs
                        # from the walk and go to next dir.
                        #
                        del subdirs[:]
                        continue
                    for filename in files:
                        fullpath = os.path.join(dirpath, filename)
                        if (    self._file_is_found(fullpath) and 
                                os.path.exists(fullpath)):
                            yield fullpath
                    if not self.recurse:
                        break

    def _file_is_found(self, filename):
        """ Should this file be "found" according to the search rules?
        """
        # Tries to eliminate the file by all the given search rules. If the 
        # file survives until the end, it's found
        #
        root, ext = os.path.splitext(filename)

        if ext in self.ignore_extensions:
            return False

        if len(self.search_extensions) > 0:
            # If search_extensions is non-empty, only files with extensions
            # listed there can be found
            #
            if ext not in self.search_extensions:
                return False

        for ignored_pattern in self.ignore_file_patterns:
            if ignored_pattern.search(filename):
                return False

        # If search_file_patterns is non-empty, the file has to match at least
        # one of the patterns.
        #
        if (len(self.search_file_patterns) > 0 and
            not any(p.search(filename) for p in self.search_file_patterns)
            ):
            return False

        return True


if __name__ == '__main__':
    import sys
    ff = FileFinder(sys.argv[1:], ignore_dirs=[], recurse=True)
    print(list(ff.files()))

