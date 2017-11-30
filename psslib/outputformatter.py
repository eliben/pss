#-------------------------------------------------------------------------------
# pss: outputformatter.py
#
# OutputFormatter interface.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import sys


class OutputFormatter(object):
    """ This is an abstract interface, to be implemented by output formatting
        classes. Individual methods that must be implemented are documented
        below. Note that some have default implementations (i.e. do not raise
        NotImplementedError)

        The pss driver expects an object adhering to this interface to do its
        output.
    """
    def start_matches_in_file(self, filename):
        """ Called when a sequences of matches from some file is about to be
            output. filename is the name of the file in which the matches were
            found.
        """
        raise NotImplementedError()

    def end_matches_in_file(self, filename):
        """ Called when the matches for a file have finished.
        """
        pass

    def matching_line(self, matchresult, filename):
        """ Called to emit a matching line, with a matchresult.MatchResult
            object.
        """
        raise NotImplementedError()

    def context_line(self, line, lineno, filename):
        """ Called to emit a context line.
        """
        pass

    def context_separator(self):
        """ Called to emit a "context separator" - line between non-adjacent
            context lines.
        """
        pass

    def binary_file_matches(self, msg):
        """ Called to emit a simple message inside the matches for some file.
        """
        raise NotImplementedError()

    def found_filename(self, filename):
        """ Called to emit a found filename when pss runs in file finding mode
            instead of line finding mode (emitting only the found files and not
            matching their contents).
        """
        raise NotImplementedError()
