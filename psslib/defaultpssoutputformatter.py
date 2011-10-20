#-------------------------------------------------------------------------------
# pss: outputformatter.py
#
# DefaultPssOutputFormatter - the default output formatter used by pss.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import sys

from .outputformatter import OutputFormatter
from .py3compat import tostring
from . import colorama


class DefaultPssOutputFormatter(OutputFormatter):
    """ The default output formatter used by pss.
    """
    def __init__(self,
            do_colors=True,
            prefix_filename_to_file_matches=True,
            show_column_of_first_match=False,
            stream=None):
        self.do_colors = do_colors
        self.prefix_filename_to_file_matches = prefix_filename_to_file_matches
        self.show_column_of_first_match = show_column_of_first_match
        self.style_filename = colorama.Fore.MAGENTA + colorama.Style.BRIGHT
        self.style_match = colorama.Fore.BLACK + colorama.Back.YELLOW

        colorama.init()

        # It's important to take sys.stdout after the call to colorama.init(),
        # because colorama.init() assigns a wrapped stream to sys.stdout and 
        # we need this wrapped stream to have colors
        #
        self.stream = stream or sys.stdout

    def start_matches_in_file(self, filename):
        if self.prefix_filename_to_file_matches:
            self._emit_colored(filename, self.style_filename)
            self._emitline()

    def end_matches_in_file(self, filename):
        self._emitline()

    def matching_line(self, matchresult):
        self._emit('%s:' % matchresult.matching_lineno)
        first_match_range = matchresult.matching_column_ranges[0]
        if self.show_column_of_first_match:
            self._emit('%s:' % first_match_range[0])

        # Emit the chunk before the first matching chunk
        line = matchresult.matching_line
        self._emit(line[:first_match_range[0]])
        # Now emit the matching chunks (colored), along with the non-matching
        # chunks that come after them
        for i, (match_start, match_end) in enumerate(
                matchresult.matching_column_ranges):
            self._emit_colored(line[match_start:match_end], self.style_match)
            if i == len(matchresult.matching_column_ranges) - 1:
                chunk = line[match_end:]
            else:
                next_start = matchresult.matching_column_ranges[i + 1][0]
                chunk = line[match_end:next_start]
            self._emit(chunk)

    def context_line(self, line, lineno):
        self._emit('%s-' % lineno)
        if self.show_column_of_first_match:
            self._emit('1-')
        self._emit(line)

    def context_separator(self):
        self._emitline('--')

    def found_filename(self, filename):
        self._emitline(filename)

    def binary_file_matches(self, msg):
        self._emitline(msg)
        
    def _emit(self, str):
        """ Write the string to the stream.
        """
        self.stream.write(tostring(str))

    def _emit_colored(self, str, style):
        """ Emit the given string with the given colorama style.
        """
        if self.do_colors:
            self._emit(style)
        self._emit(str)
        if self.do_colors:
            self._emit(colorama.Style.RESET_ALL)

    def _emitline(self, line=''):
        self._emit(line + '\n')
        

