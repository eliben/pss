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

from .utils import istextfile


class FileFinder(object):
    def __init__(self,
            roots,
            recurse=True,
            ignore_dirs=[],
            find_only_text_files=False,
            search_extensions=[],
            ignore_extensions=[],
            search_patterns=[],
            ignore_patterns=[],
            filter_include_patterns=[],
            filter_exclude_patterns=[]):
        """ Create a new FileFinder. The parameters are the "search rules"
            that dictate which files are found.

            roots:
                Root files/directories from which the search will start

            recurse:
                Should I recurse into sub-directories?

            ignore_dirs:
                Iterable of directory names that will be ignored during the
                search

            find_only_text_files:
                If True, uses a heuristic to determine which files are text
                and which are binary, and ignores the binary files.
                Warning: this option makes FileFinder actually open the files
                and read a portion from them, so it is quite slow.

            search_extensions:
            search_patterns:
                We look for either known extensions (sequences of strings) or
                matching patterns (sequence of regexes).
                If neither of these is specified, all extensions & patterns can
                be found (assuming they're not filtered out by other criteria).
                If either is specified, then the file name should match either
                one of the extensions or one of the patterns.

            ignore_extensions:
            ignore_patterns:
                Extensions and patterns to ignore. Take precedence over search_
                parameters.

            filter_include_patterns:
                Filtering: applied as logical AND with the search criteria.
                If non-empty, only files with names matching these pattens will
                be found. If empty, no pattern restriction is applied.

            filter_exclude_patterns:
                Files with names matching these patterns will never be found.
                Overrides all include rules.
        """
        # Prepare internal data structures from the parameters
        self.roots = roots
        self.recurse = recurse
        self.search_extensions = set(search_extensions)
        self.ignore_extensions = set(ignore_extensions)
        self.search_pattern = self._merge_regex_patterns(search_patterns)
        self.ignore_pattern = self._merge_regex_patterns(ignore_patterns)
        self.filter_include_pattern = self._merge_regex_patterns(
                                                filter_include_patterns)
        self.filter_exclude_pattern = self._merge_regex_patterns(
                                                filter_exclude_patterns)

        # Distinguish between dirs (like "foo") and paths (like "foo/bar")
        # to ignore.
        self.ignore_dirs = set()
        self.ignore_paths = set()
        for d in ignore_dirs:
            if os.sep in d:
                self.ignore_paths.add(d)
            else:
                self.ignore_dirs.add(d)

        self.find_only_text_files = find_only_text_files

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
                    if self._should_ignore_dir(dirpath):
                        # This dir should be ignored, so remove all its subdirs
                        # from the walk and go to next dir.
                        del subdirs[:]
                        continue
                    for filename in files:
                        fullpath = os.path.join(dirpath, filename)
                        if (    self._file_is_found(fullpath) and
                                os.path.exists(fullpath)):
                            yield fullpath
                    if not self.recurse:
                        break

    def _merge_regex_patterns(self, patterns):
        """ patterns is a sequence of strings describing regexes. Merge
            them into a single compiled regex.
        """
        if len(patterns) == 0:
            return None
        one_pattern = '|'.join('(?:{0})'.format(p) for p in patterns)
        return re.compile(one_pattern)

    def _should_ignore_dir(self, dirpath):
        """ Should the given directory be ignored?
        """
        if os.path.split(dirpath)[1] in self.ignore_dirs:
            return True
        elif len(self.ignore_paths) > 0:
            # If we have paths to ignore, things are more difficult...
            for ignored_path in self.ignore_paths:
                found_i = dirpath.rfind(ignored_path)
                if (found_i == 0 or (
                    found_i > 0 and dirpath[found_i - 1] == os.sep)
                    ):
                    return True
        return False

    def _file_is_found(self, filename):
        """ Should this file be "found" according to the search rules?
        """
        # Tries to eliminate the file by all the given search rules. If the
        # file survives until the end, it's found
        root, ext = os.path.splitext(filename)

        # The ignores take precedence.
        if (ext in self.ignore_extensions or
            self.ignore_pattern and self.ignore_pattern.search(filename)
            ):
            return False

        # Try to find a match either in search_extensions OR search_pattern.
        # If neither is specified, we have a match by definition.
        have_match = False
        if not self.search_extensions and not self.search_pattern:
            # Both empty: means all extensions and patterns are interesting.
            have_match = True
        if self.search_extensions and ext in self.search_extensions:
            have_match = True
        if self.search_pattern and self.search_pattern.search(filename):
           have_match = True

        if not have_match:
            return False

        # Now onto filters. Only files matches that don't trigger the exclude
        # filters and do trigger the include filters (if any exists) go through.
        if (self.filter_exclude_pattern and
            self.filter_exclude_pattern.search(filename)
            ):
            return False

        if (self.filter_include_pattern and
            not self.filter_include_pattern.search(filename)
            ):
            return False

        # If find_only_text_files, open the file and try to determine whether
        # it's text or binary.
        if self.find_only_text_files:
            try:
                with open(filename, 'rb') as f:
                    if not istextfile(f):
                        return False
            except OSError:
                # If there's a problem opening or reading the file, we
                # don't need it.
                return False

        return True


if __name__ == '__main__':
    import sys
    ff = FileFinder(sys.argv[1:], ignore_dirs=[], recurse=True)
    print(list(ff.files()))

