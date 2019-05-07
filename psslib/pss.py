#-------------------------------------------------------------------------------
# pss: pss.py
#
# Top-level script. Run without arguments or with -h to see usage help.
# To actually run it, import and invoke 'main' from a runnable script
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
from __future__ import print_function
import os, sys
import optparse


from psslib import __version__
from psslib.driver import (pss_run, TYPE_MAP,
        IGNORED_DIRS, IGNORED_FILE_PATTERNS, PssOnlyFindFilesOption)


def main(argv=sys.argv, output_formatter=None):
    """ Main pss

        argv:
            Program arguments, similar to sys.argv

        output_formatter:
            An OutputFormatter object to emit output to. Set to None for
            the default.

        return:
            Return code to be used when exiting to system.
            0: Match found or help/version printed. 1: No match. 2: Error.
    """
    try:
        options, args, optparser = parse_cmdline(argv[1:])
    except HelpOrVersionPrinted:
        return 0
    except SystemExit:
        return 2

    # Handle the various "only find files" options.
    #
    only_find_files = False
    only_find_files_option = PssOnlyFindFilesOption.ALL_FILES
    search_pattern_expected = True

    if options.find_files:
        only_find_files = True
        search_pattern_expected = False
    elif options.find_files_matching_patterns:
        only_find_files = True
        search_pattern_expected = False
        options.include_patterns = options.find_files_matching_patterns
    elif options.find_files_with_matches:
        only_find_files = True
        only_find_files_option = PssOnlyFindFilesOption.FILES_WITH_MATCHES
    elif options.find_files_without_matches:
        only_find_files = True
        only_find_files_option = PssOnlyFindFilesOption.FILES_WITHOUT_MATCHES

    # The --match option sets the pattern explicitly, so it's not expected
    # as an argument.
    if options.match:
        search_pattern_expected = False

    # Handle the various --help options, or just print help if pss is called
    # without arguments.
    if options.help_types:
        print_help_types()
        return 0
    elif options.show_type_list:
        show_type_list()
        return 0
    elif len(args) == 0 and search_pattern_expected:
        try:
            optparser.print_help()
        except HelpOrVersionPrinted:
            pass
        print(DESCRIPTION_AFTER_USAGE)
        return 0

    # Unpack args. If roots are not specified, the current directory is the
    # only root. If no search pattern is expected, the whole of 'args' is roots.
    #
    if not search_pattern_expected:
        pattern = options.match or None
        roots = args
    else:
        pattern = args[0]
        roots = args[1:]
    if len(roots) == 0:
        roots = ['.']

    # Partition the type list to included types (--<type>) and excluded types
    # (--no<type>)
    #
    include_types = []
    exclude_types = []
    for typ in getattr(options, 'typelist', []):
        if typ.startswith('no'):
            exclude_types.append(typ[2:])
        else:
            include_types.append(typ)

    # If the context option is specified, it overrides both after-context
    # and before-context
    #
    ncontext_before = options.before_context
    ncontext_after = options.after_context
    if options.context is not None:
        ncontext_before = ncontext_after = options.context

    add_ignored_dirs = _splice_comma_names(options.ignored_dirs or [])
    remove_ignored_dirs = _splice_comma_names(options.noignored_dirs or [])

    # Finally, invoke pss_run with the default output formatter
    #
    try:
        match_found = pss_run(
                roots=roots,
                pattern=pattern,
                output_formatter=output_formatter,
                only_find_files=only_find_files,
                only_find_files_option=only_find_files_option,
                search_all_types=options.all_types,
                search_all_files_and_dirs=options.unrestricted,
                add_ignored_dirs=add_ignored_dirs,
                remove_ignored_dirs=remove_ignored_dirs,
                recurse=options.recurse,
                textonly=options.textonly,
                include_patterns=options.include_patterns,
                exclude_patterns=options.exclude_patterns,
                include_types=include_types,
                exclude_types=exclude_types,
                ignore_case=options.ignore_case,
                smart_case=options.smart_case,
                invert_match=options.invert_match,
                whole_words=options.word_regexp,
                literal_pattern=options.literal,
                max_match_count=options.max_count,
                do_colors=options.do_colors,
                match_color_str=options.color_match,
                filename_color_str=options.color_filename,
                lineno_color_str=options.color_lineno,
                do_break=options.do_break,
                do_heading=options.do_heading,
                prefix_filename_to_file_matches=options.prefix_filename,
                show_line_of_match=options.show_line,
                show_column_of_first_match=options.show_column,
                universal_newlines=options.universal_newlines,
                ncontext_before=ncontext_before,
                ncontext_after=ncontext_after)
    except KeyboardInterrupt:
        print('<<interrupted - exiting>>')
        return 2
    except Exception as err:
        print('<<unexpected error: %s>>' % err)
        return 2
    else:
        return 0 if match_found else 1


DESCRIPTION = r'''
Search for the pattern in each source file, starting with the
current directory and its sub-directories, recursively. If
[files] are specified, only these files/directories are searched.

Only files with known extensions are searched, and this can be
configured by providing --<type> options. For example, --python
will search all Python files, and "--lisp --scheme" will search
all Lisp and all Scheme files. By default, all known file types
are searched.

Run with --help-types for more help on how to select file types.
'''.lstrip()


def _ignored_dirs_as_string():
    s = ['    ']
    for i, dir in enumerate(sorted(IGNORED_DIRS)):
        s.append('%-13s' % dir)
        if i % 4 == 3:
            s.append('\n    ')
    return ' '.join(s)


DESCRIPTION_AFTER_USAGE = r'''
By default, the following directories and everything below them is
ignored:

%s

To manually control which directories are ignored, use the --ignore-dir
and --noignore-dir options. Specify --unrestricted if you don't want any
directory to be ignored.

Additionally, files matching these (regexp) patterns are ignored:

      %s

pss version %s
''' % ( _ignored_dirs_as_string(),
        '\n      '.join(IGNORED_FILE_PATTERNS),
        __version__,)


def parse_cmdline(cmdline_args):
    """ Parse the list of command-line options and arguments and return a
        triple: options, args, parser -- the first two being the result of
        OptionParser.parse_args, and the third the parser object itself.`
    """
    optparser = PssOptionParser(
        usage='usage: %prog [options] <pattern> [files]',
        description=DESCRIPTION,
        prog='pss',
        version='pss %s' % __version__)

    optparser.add_option('--help-types',
        action='store_true', dest='help_types',
        help='Display supported file types')

    # This option is for internal usage by the bash completer, so we're hiding
    # it from the --help output
    optparser.add_option('--show-type-list',
        action='store_true', dest='show_type_list',
        help=optparse.SUPPRESS_HELP)

    group_searching = optparse.OptionGroup(optparser, 'Searching')
    group_searching.add_option('-i', '--ignore-case',
        action='store_true', dest='ignore_case', default=False,
        help='Ignore case distinctions in the pattern')
    group_searching.add_option('--smart-case',
        action='store_true', dest='smart_case', default=False,
        help='Ignore case distinctions in the pattern, only if the pattern '
        'contains no upper case. Ignored if -i is specified')
    group_searching.add_option('-v', '--invert-match',
        action='store_true', dest='invert_match', default=False,
        help='Invert match: show non-matching lines')
    group_searching.add_option('-w', '--word-regexp',
        action='store_true', dest='word_regexp', default=False,
        help='Force the pattern to match only whole words')
    group_searching.add_option('-Q', '--literal',
        action='store_true', dest='literal', default=False,
        help='Quote all metacharacters; the pattern is literal')
    group_searching.add_option('-U', '--universal-newlines',
        action='store_true', dest='universal_newlines', default=False,
        help='Use PEP 278 universal newline support when opening files')
    optparser.add_option_group(group_searching)

    group_output = optparse.OptionGroup(optparser, 'Search output')
    group_output.add_option('--match',
        action='store', dest='match', metavar='PATTERN',
        help='Specify the search pattern explicitly')
    group_output.add_option('-m', '--max-count',
        action='store', dest='max_count', metavar='NUM', default=sys.maxsize,
        type='int', help='Stop searching in each file after NUM matches')
    group_output.add_option('--with-filename',
        action='store_true', dest='prefix_filename', default=True,
        help=' '.join(r'''Print the filename before matches (default). If
        --noheading is specified, the filename will be prepended to each
        matching line. Otherwise it is printed once for all the matches
        in the file.'''.split()))
    group_output.add_option('--no-filename',
        action='store_false', dest='prefix_filename',
        help='Suppress printing the filename before matches')
    group_output.add_option('--line',
        action='store_true', dest='show_line', default=True,
        help='Print the line number before matches (default)')
    group_output.add_option('--noline',
        action='store_false', dest='show_line',
        help='Suppress printing the line number before matches')
    group_output.add_option('--column',
        action='store_true', dest='show_column',
        help='Show the column number of the first match')
    group_output.add_option('--nocolumn',
        action='store_false', dest='show_column',
        help='Suppress showing the column number of the first match (default)')
    group_output.add_option('-A', '--after-context',
        action='store', dest='after_context', metavar='NUM', default=0,
        type='int', help='Print NUM lines of context after each match')
    group_output.add_option('-B', '--before-context',
        action='store', dest='before_context', metavar='NUM', default=0,
        type='int', help='Print NUM lines of context before each match')
    group_output.add_option('-C', '--context',
        action='store', dest='context', metavar='NUM', type='int',
        help='Print NUM lines of context before and after each match')
    group_output.add_option('--color',
        action='store_true', dest='do_colors', default=sys.stdout.isatty(),
        help='Highlight the matching text')
    group_output.add_option('--nocolor',
        action='store_false', dest='do_colors',
        help='Do not highlight the matching text (this is the default when output is redirected)')
    group_output.add_option('--color-match', metavar='FORE,BACK,STYLE',
        action='store', dest='color_match',
        help='Set the color for matches')
    group_output.add_option('--color-filename', metavar='FORE,BACK,STYLE',
        action='store', dest='color_filename',
        help='Set the color for emitted filenames')
    group_output.add_option('--color-lineno', metavar='FORE,BACK,STYLE',
        action='store', dest='color_lineno',
        help='Set the color for line numbers')
    group_output.add_option('--nobreak',
        action='store_false', dest='do_break', default=sys.stdout.isatty(),
        help='Print no break between results from different files')
    group_output.add_option('--noheading',
        action='store_false', dest='do_heading', default=sys.stdout.isatty(),
        help="Print no file name heading above each file's results")
    optparser.add_option_group(group_output)

    group_filefinding = optparse.OptionGroup(optparser, 'File finding')
    group_filefinding.add_option('-f',
        action='store_true', dest='find_files',
        help='Only print the names of found files. The pattern must not be specified')
    group_filefinding.add_option('-g',
        action='append', dest='find_files_matching_patterns',
        metavar='REGEX', default=[],
        help='Same as -f, but only print files matching REGEX')
    group_filefinding.add_option('-l', '--files-with-matches',
        action='store_true', dest='find_files_with_matches',
        help='Only print the names of found files that have matches for the pattern')
    group_filefinding.add_option('-L', '--files-without-matches',
        action='store_true', dest='find_files_without_matches',
        help='Only print the names of found files that have no matches for the pattern')
    optparser.add_option_group(group_filefinding)

    group_inclusion = optparse.OptionGroup(optparser, 'File inclusion/exclusion')
    group_inclusion.add_option('-a', '--all-types',
        action='store_true', dest='all_types',
        help='All file types are searched')
    group_inclusion.add_option('-u', '--unrestricted',
        action='store_true', dest='unrestricted',
        help='All files are searched, including those in ignored directories')
    group_inclusion.add_option('--ignore-dir',
        action='append', dest='ignored_dirs', metavar='name',
        help='Add directory to the list of ignored dirs')
    group_inclusion.add_option('--noignore-dir',
        action='append', dest='noignored_dirs', metavar='name',
        help='Remove directory from the list of ignored dirs')
    group_inclusion.add_option('-r', '-R', '--recurse',
        action='store_true', dest='recurse', default=True,
        help='Recurse into subdirectories (default)')
    group_inclusion.add_option('-n', '--no-recurse',
        action='store_false', dest='recurse',
        help='Do not recurse into subdirectories')
    group_inclusion.add_option('-t', '--textonly', '--nobinary',
        action='store_true', dest='textonly', default=False,
        help='''Restrict the search to only textual files.
        Warning: with this option the search is likely to run much slower''')
    group_inclusion.add_option('-G', '--include-pattern',
        action='append', dest='include_patterns', metavar='REGEX', default=[],
        help='Only search files that match REGEX')
    group_inclusion.add_option('--exclude-pattern',
        action='append', dest='exclude_patterns', metavar='REGEX', default=[],
        help='Exclude files that match REGEX')
    optparser.add_option_group(group_inclusion)

    # Parsing --<type> and --no<type> options for all supported types is
    # done with a callback action. The callback function stores a list
    # of all type options in the typelist attribute of the options.
    #
    def type_option_callback(option, opt_str, value, parser):
        optname = opt_str.lstrip('-')
        if hasattr(parser.values, 'typelist'):
            parser.values.typelist.append(optname)
        else:
            parser.values.typelist = [optname]

    for t in TYPE_MAP:
        optparser.add_option('--' + t,
            help=optparse.SUPPRESS_HELP,
            action='callback',
            callback=type_option_callback)
        optparser.add_option('--no' + t,
            help=optparse.SUPPRESS_HELP,
            action='callback',
            callback=type_option_callback)

    options, args = optparser.parse_args(cmdline_args)
    return options, args, optparser


HELP_TYPES_PREAMBLE = r'''
The following types are supported.  Each type enables searching
in several file extensions or name regexps.  --<type> includes
the type in search and --no<type> excludes it.
'''.lstrip()


def print_help_types():
    print(HELP_TYPES_PREAMBLE)

    for typ in sorted(TYPE_MAP):
        typestr = '--[no]%s' % typ
        print('    %-21s' % typestr, end='')
        print(' '.join(TYPE_MAP[typ].extensions + TYPE_MAP[typ].patterns))
    print()


def show_type_list():
    print(' '.join(('--%s' % typ) for typ in TYPE_MAP))


def _splice_comma_names(namelist):
    """ Given a list of names, some of the names can be comma-separated lists.
        Return a new list of single names (names in comma-separated lists are
        spliced into the list).
    """
    newlist = []
    for name in namelist:
        if ',' in name:
            newlist.extend(name.split(','))
        else:
            newlist.append(name)
    return newlist


class PssOptionParser(optparse.OptionParser):
    """Option parser that separates using --help and --version from
       using invalid options.

       By default optparse uses SystemExit with both. This parser uses custom
       HelpOrVersionPrinted exception with --help and --version.
    """
    def print_version(self, file=None):
        optparse.OptionParser.print_version(self, file)
        raise HelpOrVersionPrinted()

    def print_help(self):
        optparse.OptionParser.print_help(self)
        print(DESCRIPTION_AFTER_USAGE)
        raise HelpOrVersionPrinted()


class HelpOrVersionPrinted(Exception):
    pass
