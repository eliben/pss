#-------------------------------------------------------------------------------
# pss: driver.py
#
# Top-level functions and data used to execute pss.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import os
import re
import sys

from .filefinder import FileFinder
from .contentmatcher import ContentMatcher
from .matchresult import MatchResult
from .defaultpssoutputformatter import DefaultPssOutputFormatter
from .utils import istextfile
from .py3compat import str2bytes


TYPE_EXTENSION_MAP = {
        'actionscript':     ['.as', '.mxml'],
        'ada':              ['.ada', '.adb', '.ads'],
        'batch':            ['.bat', '.cmd'],
        'asm':              ['.asm', '.s'],
        'cc':               ['.c', '.h', '.xs'],
        'cfmx':             ['.cfc', '.cfm', '.cfml'],
        'cpp':              ['.cpp', '.cc', '.cxx', '.m', '.hpp', '.hh', '.h', '.hxx'],
        'csharp':           ['.cs'],
        'css':              ['.css'],
        'elisp':            ['.elisp'],
        'erlang':           ['.erl', '.hrl'],
        'fortran':          ['.f', '.f77', '.f90', '.f95', '.f03', '.for', '.ftn', '.fpp'],
        'haskell':          ['.hs', '.lhs'],
        'hh':               ['.h'],
        'html':             ['.htm', '.html', '.shtml', '.xhtml'],
        'java':             ['.java', '.properties'],
        'js':               ['.js'],
        'jsp':              ['.jsp'],
        'lisp':             ['.lisp', '.lsp', '.cl'],
        'lua':              ['.lua'],
        'mason':            ['.mas', '.mthml', '.mpl', '.mtxt'],
        'objc':             ['.m', '.h'],
        'objcpp':           ['.mm', '.h'],
        'ocaml':            ['.ml', '.mli'],
        'parrot':           ['.pir', '.pasm', '.pmc', '.ops', '.pod', '.pg', '.tg'],
        'perl':             ['.pl', '.pm', '.pod', '.t'],
        'php':              ['.php', '.phpt', '.php3', '.php4', '.php5', '.phtml'],
        'plone':            ['.pt', '.cpt', '.metadata', '.cpy', '.py'],
        'python':           ['.py'],
        'ruby':             ['.rb', '.rhtml', '.rjs', '.rxml', '.erb', '.rake'],
        'scala':            ['.scala'],
        'scheme':           ['.scm', '.ss'],
        'shell':            ['.sh', '.bash', '.csh', '.tcsh', '.ksh', '.zsh'],
        'smalltalk':        ['.st'],
        'sql':              ['.sql', '.ctl'],
        'tcl':              ['.tck', '.itcl', '.itk'],
        'tex':              ['.tex', '.cls', '.sty'],
        'tt':               ['.tt', '.tt2', '.ttml'],
        'vb':               ['.bas', '.cls', '.frm', '.ctl', '.vb', '.resx'],
        'vim':              ['.vim'],
        'xml':              ['.xml', '.dtd', '.xslt', '.ent'],
        'yaml':             ['.yaml', '.yml'],
}
ALL_KNOWN_EXTENSIONS = set(
        ext for extensions in TYPE_EXTENSION_MAP.values() 
            for ext in extensions)

IGNORED_DIRS = set([   
    'blib', '_build', '.bzr', '.cdv', 'cover_db',
    'CVS', '_darcs', '~.dep', '~.dot', '.git', '.hg', '~.nib', 
    '.pc', '~.plst', 'RCS', 'SCCS', '_sgbak', '.svn'])

IGNORED_FILE_PATTERNS = set([r'~$', r'#.+#$', r'[._].*\.swp$', r'core\.\d+$'])


class PssOnlyFindFilesOption:
    """ Option to specify how to "only find files"
    """
    ALL_FILES, FILES_WITH_MATCHES, FILES_WITHOUT_MATCHES = range(3)


def pss_run(roots,
        pattern=None,
        output_formatter=None,
        only_find_files=False,
        only_find_files_option=PssOnlyFindFilesOption.ALL_FILES,
        search_all_types=False,
        search_all_files_and_dirs=False,
        add_ignored_dirs=[],
        remove_ignored_dirs=[],
        recurse=True,
        type_pattern=None, # for -G and -g
        include_types=[],  # empty means all known types are included
        exclude_types=[],
        ignore_case=False,
        smart_case=False,
        invert_match=False,
        whole_words=False,
        literal_pattern=False,
        max_match_count=sys.maxsize,
        do_colors=True,
        prefix_filename_to_file_matches=True,
        show_column_of_first_match=False,
        ncontext_before=0,
        ncontext_after=0,
        ):
    """ The main pss invocation function - handles all PSS logic.
        For documentation of options, see the --help output of the pss script,
        and study how its command-line arguments are parsed and passed to
        this function. Besides, most options are passed verbatim to submodules
        and documented there. I don't like to repeat myself too much :-)
    """
    # Set up a default output formatter, if none is provided
    #
    if output_formatter is None:
        output_formatter = DefaultPssOutputFormatter(
            do_colors,
            prefix_filename_to_file_matches,
            show_column_of_first_match)

    # Set up the FileFinder
    #
    if search_all_files_and_dirs:
        ignore_dirs = set()
    else:
        # gotta love set arithmetic
        ignore_dirs = ((IGNORED_DIRS | set(add_ignored_dirs))
                        - set(remove_ignored_dirs))

    search_extensions = set()
    ignore_extensions = set()
    search_file_patterns = set()
    ignore_file_patterns = set()

    if type_pattern is not None:
        search_file_patterns.add(type_pattern)

    if not search_all_files_and_dirs and not search_all_types:
        if include_types:
            search_extensions.clear()
            for typ in include_types:
                search_extensions.update(TYPE_EXTENSION_MAP[typ])
        else:
            for ext in TYPE_EXTENSION_MAP.values():
                search_extensions.update(ext)
        for typ in exclude_types:
            ignore_extensions.update(TYPE_EXTENSION_MAP[typ])
        ignore_file_patterns = IGNORED_FILE_PATTERNS
    else:
        # An empty search_extensions means all extensions are searched
        pass

    filefinder = FileFinder(
            roots=roots,
            recurse=recurse,
            ignore_dirs=ignore_dirs,
            search_extensions=search_extensions,
            ignore_extensions=ignore_extensions,
            search_file_patterns=search_file_patterns,
            ignore_file_patterns=ignore_file_patterns)

    # Set up the content matcher
    #

    if pattern is None:
        pattern = b''
    else:
        pattern = str2bytes(pattern)

    if (    not ignore_case and 
            (smart_case and not _pattern_has_uppercase(pattern))):
        ignore_case = True

    matcher = ContentMatcher(
            pattern=pattern,
            ignore_case=ignore_case,
            invert_match=invert_match,
            whole_words=whole_words,
            literal_pattern=literal_pattern,
            max_match_count=max_match_count)

    # All systems go...
    #
    for filepath in filefinder.files():
        # If only_find_files is requested and no special option provided,
        # this is kind of 'find -name'
        if (    only_find_files and 
                only_find_files_option == PssOnlyFindFilesOption.ALL_FILES):
            output_formatter.found_filename(filepath)
            continue
        # The main path: do matching inside the file.
        # Some files appear to be binary - they are not of a known file type
        # and the heuristic istextfile says they're binary. For these files 
        # we try to find a single match and then simply report they're binary
        # files with a match. For other files, we let ContentMatcher do its
        # full work.
        #
        with open(filepath, 'rb') as fileobj:
            if not istextfile(fileobj):
                # istextfile does some reading on fileobj, so rewind it
                fileobj.seek(0)
                matches = list(matcher.match_file(fileobj, max_match_count=1))
                if matches:
                    output_formatter.binary_file_matches(
                            'Binary file %s matches\n' % filepath)
                continue
            # istextfile does some reading on fileobj, so rewind it
            fileobj.seek(0)
            # run, my little matcher, run!
            matches = list(matcher.match_file(fileobj))

            # If only files are to be found either with or without matches...
            if only_find_files:
                found = (
                    (   matches and 
                        only_find_files_option == PssOnlyFindFilesOption.FILES_WITH_MATCHES)
                    or
                    (   not matches and 
                        only_find_files_option == PssOnlyFindFilesOption.FILES_WITHOUT_MATCHES))
                if found:
                    output_formatter.found_filename(filepath)
                continue

            # This is the "normal path" when we examine and display the matches
            # inside the file.
            if not matches:
                # Nothing to see here... move along
                continue
            output_formatter.start_matches_in_file(filepath)
            if ncontext_before > 0 or ncontext_after > 0:
                # If context lines should be printed, we have to read in the
                # file line by line, marking which lines belong to context,
                # which are matches, and which aren't interesting.
                # _build_match_context_dict is used to create a dictionary
                # that tells us for each line what category it belongs to
                #
                fileobj.seek(0)
                match_context_dict = _build_match_context_dict(
                        matches, ncontext_before, ncontext_after)
                # For being able to correctly emit context separators between 
                # non-adjacent chunks of context, these flags are maintained:
                #   prev_was_blank: the previous line was blank
                #   had_context: we already had some context printed before
                #
                prev_was_blank = False
                had_context = False
                for n, line in enumerate(fileobj):
                    n += 1
                    # Find out whether this line is a match, context or neither,
                    # and act accordingly
                    result, match = match_context_dict.get(n, (None, None))
                    if result is None:
                        prev_was_blank = True
                        continue
                    elif result == LINE_MATCH:
                        output_formatter.matching_line(match)
                    elif result == LINE_CONTEXT:
                        if prev_was_blank and had_context:
                            output_formatter.context_separator()
                        output_formatter.context_line(line, n)
                        had_context = True
                    prev_was_blank = False
            else:
                # just show the matches without considering context
                for match in matches:
                    output_formatter.matching_line(match)
            output_formatter.end_matches_in_file(filepath)


def _known_file_type(filename):
    """ Is the given file something we know about?
        Judges solely based on the file name and extension.
    """
    if os.path.splitext(filename)[1] in ALL_KNOWN_EXTENSIONS:
        return True
    else:
        return False


def _pattern_has_uppercase(pattern):
    """ Check whether the given regex pattern has uppercase letters to match
    """
    # Somewhat rough - check for uppercase chars not following an escape 
    # char (which may mean valid regex flags like \A or \B)
    skipnext = False
    for c in pattern:
        if skipnext:
            skipnext = False
            continue
        elif c == '\\': 
            skipnext = True
        else:
            if c >= 'A' and c <= 'Z':
                return True
    return False


LINE_MATCH, LINE_CONTEXT = range(2)

    
def _build_match_context_dict(matches, ncontext_before, ncontext_after):
    """ Given a list of MatchResult objects and number of context lines before
        and after a match, build a dictionary that maps line numbers to 
        (line_kind, data) pairs. line_kind is either LINE_MATCH or LINE_CONTEXT
        and data holds the match object for LINE_MATCH.
    """
    d = {}
    for match in matches:
        # Take care to give LINE_MATCH entries priority over LINE_CONTEXT
        lineno = match.matching_lineno
        d[lineno] = LINE_MATCH, match

        context_start = lineno - ncontext_before
        context_end = lineno + ncontext_after
        for ncontext in range(context_start, context_end + 1):
            if ncontext not in d:
                d[ncontext] = LINE_CONTEXT, None
    return d


