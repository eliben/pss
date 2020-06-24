#-------------------------------------------------------------------------------
# pss: driver.py
#
# Top-level functions and data used to execute pss.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import collections
import sys

from .filefinder import FileFinder
from .contentmatcher import ContentMatcher
from .defaultpssoutputformatter import DefaultPssOutputFormatter
from .utils import istextfile
from .py3compat import str2bytes

TypeSpec = collections.namedtuple('TypeSpec', ['extensions', 'patterns'])

TYPE_MAP = {
    'actionscript':
        TypeSpec(['.as', '.mxml'], []),
    'ada':
        TypeSpec(['.ada', '.adb', '.ads'], []),
    'asm':
        TypeSpec(['.asm', '.s', '.S'], []),
    'batch':
        TypeSpec(['.bat', '.cmd'], []),
    'bazel':
        TypeSpec(['.bzl'], ['BUILD']),
    'cc':
        TypeSpec(['.c', '.h', '.xs'], []),
    'cfg':
        TypeSpec(['.cfg', '.conf', '.config'], []),
    'cfmx':
        TypeSpec(['.cfc', '.cfm', '.cfml'], []),
    'clj':
        TypeSpec(['.clj'], []),
    'clojure':
        TypeSpec(['.clj'], []),
    'cmake':
        TypeSpec(['.cmake'], ['CMake(Lists|Funcs).txt']),
    'cpp':
        TypeSpec(['.cpp', '.cc', '.cxx', '.m', '.hpp', '.hh', '.h', '.hxx'], []),
    'csharp':
        TypeSpec(['.cs'], []),
    'css':
        TypeSpec(['.css', '.less', '.scss'], []),
    'cuda':
        TypeSpec(['.cu'], []),
    'cython':
        TypeSpec(['.pyx', '.pxd', '.pyxbld'], []),
    'dart':
        TypeSpec(['.dart'], []),
    'docker':
        TypeSpec([], ['Dockerfile', 'Dockerfile\.(\w+)']),
    'elisp':
        TypeSpec(['.el', '.elisp'], []),
    'erlang':
        TypeSpec(['.erl', '.hrl'], []),
    'fortran':
        TypeSpec(['.f', '.f77', '.f90', '.F90', '.f95', '.F95', '.f03', '.for', '.ftn', '.fpp'], []),
    'go':
        TypeSpec(['.go'], []),
    'gomod':
        TypeSpec([], ['go\.mod']),
    'haskell':
        TypeSpec(['.hs', '.lhs'], []),
    'hs':
        TypeSpec(['.hs', '.lhs'], []),
    'hh':
        TypeSpec(['.h'], []),
    'html':
        TypeSpec(['.htm', '.html', '.shtml', '.xhtml'], []),
    'inc':
        TypeSpec(['.inc', '.inl'], []),
    'java':
        TypeSpec(['.java', '.properties'], []),
    'jinja2':
        TypeSpec(['.j2'], []),
    'js':
        TypeSpec(['.js', '.jsx'], []),
    'json':
        TypeSpec(['.json'], []),
    'jsp':
        TypeSpec(['.jsp'], []),
    'julia':
        TypeSpec(['.jl'], []),
    'lisp':
        TypeSpec(['.lisp', '.lsp', '.cl'], []),
    'llvm':
        TypeSpec(['.ll'], []),
    'lua':
        TypeSpec(['.lua'], []),
    'make':
        TypeSpec(['.mk'], ['[Mm]akefile']),
    'mason':
        TypeSpec(['.mas', '.mthml', '.mpl', '.mtxt'], []),
    'md':
        TypeSpec(['.md'], []),
    'objc':
        TypeSpec(['.m', '.h'], []),
    'objcpp':
        TypeSpec(['.mm', '.h'], []),
    'ocaml':
        TypeSpec(['.ml', '.mli'], []),
    'opencl':
        TypeSpec(['.cl'], []),
    'parrot':
        TypeSpec(['.pir', '.pasm', '.pmc', '.ops', '.pod', '.pg', '.tg'], []),
    'perl':
        TypeSpec(['.pl', '.pm', '.pod', '.t'], []),
    'php':
        TypeSpec(['.php', '.phpt', '.php3', '.php4', '.php5', '.phtml'], []),
    'plone':
        TypeSpec(['.pt', '.cpt', '.metadata', '.cpy', '.py'], []),
    'proto':
        TypeSpec(['.proto'], []),
    'py':
        TypeSpec(['.py', '.pyw'], []),
    'python':
        TypeSpec(['.py', '.pyw'], []),
    'r':
        TypeSpec(['.R', '.Rmd'], []),
    'rake':
        TypeSpec([], ['[Rr]akefile']),
    'rst':
        TypeSpec(['.rst', '.rest'], []),
    'rb':
        TypeSpec(['.rb'], []),
    'ruby':
        TypeSpec(['.rb', '.rhtml', '.rjs', '.rxml', '.erb', '.rake', '.haml'], []),
    'scala':
        TypeSpec(['.scala'], []),
    'scheme':
        TypeSpec(['.scm', '.ss'], []),
    'scons':
        TypeSpec(['.scons'], ['SConstruct']),
    'shell':
        TypeSpec(['.sh', '.bash', '.csh', '.tcsh', '.ksh', '.zsh'], []),
    'smalltalk':
        TypeSpec(['.st'], []),
    'sql':
        TypeSpec(['.sql', '.ctl'], []),
    'tablegen':
        TypeSpec(['.td'], []),
    'tcl':
        TypeSpec(['.tck', '.itcl', '.itk'], []),
    'td':  # short-name for --tablegen
        TypeSpec(['.td'], []),
    'terraform':
        TypeSpec(['.tf', '.tfvars', '.hcl', '.tfstate'], []),
    'tex':
        TypeSpec(['.tex', '.cls', '.sty'], []),
    'toml':
        TypeSpec(['.toml'], []),
    'tt':
        TypeSpec(['.tt', '.tt2', '.ttml'], []),
    'txt':
        TypeSpec(['.txt', '.text'], []),
    'ts':
        TypeSpec(['.ts', '.tsx'], []),
    'typescript':
        TypeSpec(['.ts', '.tsx'], []),
    'vb':
        TypeSpec(['.bas', '.cls', '.frm', '.ctl', '.vb', '.resx'], []),
    'verilog':
        TypeSpec(['.v', '.sv'], []),
    'vim':
        TypeSpec(['.vim'], []),
    'vhdl':
        TypeSpec(['.vhd', '.vhdl'], []),
    'withoutext':
        TypeSpec([''], []),
    'xml':
        TypeSpec(['.xml', '.dtd', '.xslt', '.ent'], []),
    'yaml':
        TypeSpec(['.yaml', '.yml'], []),
}

IGNORED_DIRS = frozenset([
    'blib', '_build', '.bzr', '.cdv', 'cover_db', '__pycache__',
    'CVS', '_darcs', '~.dep', '~.dot', '.git', '.hg', '~.nib',
    '.pc', '~.plst', 'RCS', 'SCCS', '_sgbak', '.svn', '.tox',
    '.metadata', '.cover', '.Rproj.user', '.Rhistory', 'node_modules'])

IGNORED_FILE_PATTERNS = frozenset(
    [r'~$', r'#.+#$', r'[._].*\.swp$', r'core\.\d+$'])


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
        textonly=False,
        include_patterns=[], # for -G and -g
        exclude_patterns=[],
        include_types=[],  # empty means all known types are included
        exclude_types=[],
        ignore_case=False,
        smart_case=False,
        invert_match=False,
        whole_words=False,
        literal_pattern=False,
        max_match_count=sys.maxsize,
        do_colors=True,
        match_color_str=None,
        filename_color_str=None,
        lineno_color_str=None,
        do_break=True,
        do_heading=True,
        prefix_filename_to_file_matches=True,
        show_line_of_match=True,
        show_column_of_first_match=False,
        universal_newlines=False,
        ncontext_before=0,
        ncontext_after=0,
        ):
    """ The main pss invocation function - handles all PSS logic.

        For documentation of options, see the --help output of the pss script,
        and study how its command-line arguments are parsed and passed to
        this function. Besides, most options are passed verbatim to submodules
        and documented there. I don't like to repeat myself too much :-)

        Returns True if a match was found, False otherwise.
    """
    # Set up a default output formatter, if none is provided
    if output_formatter is None:
        output_formatter = DefaultPssOutputFormatter(
            do_colors=do_colors,
            match_color_str=match_color_str,
            filename_color_str=filename_color_str,
            lineno_color_str=lineno_color_str,
            do_heading=do_heading,
            prefix_filename_to_file_matches=prefix_filename_to_file_matches,
            show_line_of_match=show_line_of_match,
            show_column_of_first_match=show_column_of_first_match)

    # Set up the FileFinder
    if search_all_files_and_dirs:
        ignore_dirs = set()
    else:
        # gotta love set arithmetic
        ignore_dirs = ((IGNORED_DIRS | set(add_ignored_dirs))
                        - set(remove_ignored_dirs))

    search_extensions = set()
    ignore_extensions = set()
    search_patterns = set()
    ignore_patterns = set()
    # include_patterns (-g/-G) is an AND filter to the search criteria
    filter_include_patterns = set(include_patterns)
    filter_exclude_patterns = set(exclude_patterns)

    if search_all_files_and_dirs or search_all_types:
        # Don't apply restrictions
        pass
    else:
        filter_exclude_patterns |= set(IGNORED_FILE_PATTERNS)

        for typ in (include_types or TYPE_MAP):
            search_extensions.update(TYPE_MAP[typ].extensions)
            search_patterns.update(TYPE_MAP[typ].patterns)

        for typ in exclude_types:
            ignore_extensions.update(TYPE_MAP[typ].extensions)
            ignore_patterns.update(TYPE_MAP[typ].patterns)

    filefinder = FileFinder(
            roots=roots,
            recurse=recurse,
            find_only_text_files=textonly,
            ignore_dirs=ignore_dirs,
            search_extensions=search_extensions,
            ignore_extensions=ignore_extensions,
            search_patterns=search_patterns,
            ignore_patterns=ignore_patterns,
            filter_include_patterns=filter_include_patterns,
            filter_exclude_patterns=filter_exclude_patterns)

    # Set up the content matcher
    #

    if universal_newlines:
        if pattern is None:
            pattern = ''
    else:
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

    match_found = False

    # All systems go...
    #
    for filepath in filefinder.files():
        # If only_find_files is requested and no special option provided,
        # this is kind of 'find -name'
        if (    only_find_files and
                only_find_files_option == PssOnlyFindFilesOption.ALL_FILES):
            output_formatter.found_filename(filepath)
            match_found = True
            continue
        # The main path: do matching inside the file.
        # Some files appear to be binary - they are not of a known file type
        # and the heuristic istextfile says they're binary. For these files
        # we try to find a single match and then simply report they're binary
        # files with a match. For other files, we let ContentMatcher do its
        # full work.
        #
        try:
            openmode = 'rU' if universal_newlines else 'rb'
            with open(filepath, openmode) as fileobj:
                if not istextfile(fileobj):
                    # istextfile does some reading on fileobj, so rewind it
                    fileobj.seek(0)
                    matches = list(matcher.match_file(fileobj, max_match_count=1))
                    if matches:
                        output_formatter.binary_file_matches(
                                'Binary file %s matches\n' % filepath)
                        match_found = True
                    continue
                # istextfile does some reading on fileobj, so rewind it
                fileobj.seek(0)

                # If only files are to be found either with or without matches...
                if only_find_files:
                    matches = list(matcher.match_file(fileobj, max_match_count=1))
                    found = (
                        (   matches and
                            only_find_files_option == PssOnlyFindFilesOption.FILES_WITH_MATCHES)
                        or
                        (   not matches and
                            only_find_files_option == PssOnlyFindFilesOption.FILES_WITHOUT_MATCHES))
                    if found:
                        output_formatter.found_filename(filepath)
                        match_found = True
                    continue

                # This is the "normal path" when we examine and display the
                # matches inside the file.
                matches = list(matcher.match_file(fileobj))
                if not matches:
                    # Nothing to see here... move along
                    continue
                match_found =True
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
                    for n, line in enumerate(fileobj, 1):
                        # Find out whether this line is a match, context or
                        # neither, and act accordingly
                        result, match = match_context_dict.get(n, (None, None))
                        if result is None:
                            prev_was_blank = True
                            continue
                        elif result == LINE_MATCH:
                            output_formatter.matching_line(match, filepath)
                        elif result == LINE_CONTEXT:
                            if prev_was_blank and had_context:
                                output_formatter.context_separator()
                            output_formatter.context_line(line, n, filepath)
                            had_context = True
                        prev_was_blank = False
                else:
                    # just show the matches without considering context
                    for match in matches:
                        output_formatter.matching_line(match, filepath)

                if do_break:
                    output_formatter.end_matches_in_file(filepath)
        except (OSError, IOError):
            # There was a problem opening or reading the file, so ignore it.
            pass

    return match_found


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
