#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import argparse
import os, os.path
import re
import shutil
import sys
import tempfile
import textwrap

from pprint import pprint, pformat

__version__ = '0.1'

DEFAULT_BACKUP_EXTENSION = 'bak'

class ParserException (Exception): pass

def show_version ():
    msg ('{0}: version {1}'.format (os.path.basename (sys.argv[0]), __version__))
    sys.exit (0)

def errmsg (msg, indent=0, end=None):
    print ((' ' * indent * 4) + msg, file=sys.stderr, end=end)

def msg (msg, indent=0, end=None):
    print ((' ' * indent * 4) + msg, end=end)

def debug (msg, indent=0, end=None):
    print ((' ' * indent * 4) + msg, file=sys.stderr, end=end)

def get_ext (args):
    """ Find extension for backup files
    """
    if args.no_backup:
        return ''

    if args.ext is None or len (args.ext) == 0:
        return '.' + DEFAULT_BACKUP_EXTENSION

    return '.' + args.ext

def prepare_replacement (r, to_eval=False):
    """ If to_eval argument is True, then compile replace argument
        as valid Python code and return function which can be passed
        to re.sub or re.subn functions.
    """
    if not to_eval:
        return r

    def repl (m):
        return eval (r, { '__builtins__': __builtins__ }, { 'm': m })

    return repl

def prepare_pattern_data (args):
    """ Read arguments from argparse.ArgumentParser instance, and
        parse it to find correct values for arguments:
            * pattern
            * replace
            * count
        If is provided --pattern_and_replace argument, then parse
        it and return data from it.

        In other case just return data from argparse.ArgumentParser
        instance.

        Reads also string argument, and apply it to pattern.

        Returned pattern is compiled (see: re.compile).
    """

    flags = 0
    if args.ignore_case:
        flags |= re.IGNORECASE

    if args.pattern_dot_all:
        flags |= re.DOTALL

    if args.pattern_verbose:
        flags |= re.VERBOSE

    if args.pattern_multiline:
        flags |= re.MULTILINE

    if args.pattern is not None and args.replace is not None:
        if args.string:
            pattern = re.escape (args.pattern)
        else:
            pattern = args.pattern

        return re.compile (pattern, flags), args.replace, args.count or 0

    elif args.pattern_and_replace is not None:
        p = args.pattern_and_replace

        try:
            # pattern must begin with 's'
            if not p.startswith ('s'):
                raise ParserException ('Bad pattern specified: {0}'.format (args.pattern_and_replace))
            p = p[1:]

            # pattern can be suffixed with g (as global)
            if p.endswith ('g'):
                count = 0
                p = p[:-1]
            else:
                count = args.count if args.count is not None else 1

            # parse pattern
            if p.startswith ('(') and p.endswith (')'):
                pattern, replace = p[1:-1].split (')(', 1)
            elif p.startswith ('{') and p.endswith ('}'):
                pattern, replace = p[1:-1].split ('}{', 1)
            elif p.startswith ('[') and p.endswith (']'):
                pattern, replace = p[1:-1].split ('][', 1)
            elif p.startswith ('<') and p.endswith ('>'):
                pattern, replace = p[1:-1].split ('><', 1)
            else:
                delim = p[0]
                if not p.endswith (delim):
                    raise ParserException ('Bad pattern specified: {0}'.format (args.pattern_and_replace))

                p = p[1:-1]
                pattern, replace = p.split (delim, 1)
        except ValueError:
            raise ParserException ('Bad pattern specified: {0}'.format (args.pattern_and_replace))

        return re.compile (pattern, flags), replace, count
    else:
        raise ParserException ('Bad pattern specified: {0}'.format (args.pattern_and_replace))

def wrap_text (s):
    """ Make custom wrapper for passed text.

        Splits given text for lines, and for every line apply custom
        textwrap.TextWrapper settings, then return reformatted string.
    """
    w = textwrap.TextWrapper (
        width = 72,
        expand_tabs = True,
        replace_whitespace = False,
        drop_whitespace = True,
        subsequent_indent = '  ',
    )
    s = [ w.fill (line) for line in s.splitlines () ]
    return "\n".join (s)

def parse_args (args):
    """ Parse arguments passed to script, validate it, compile if needed and return.
    """
    p = argparse.ArgumentParser (
        description='Replace PATTERN with REPLACE in many files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=wrap_text ("Miscellaneous notes:\n"
            "* regular expressions engine used here is PCRE, dialect from Python\n"
            "* is required to pass either --pattern and -replace, or --pattern_and_replace argument\n"
            "* if pattern passed to --pattern_and_replace has /g modifier, it overwrites --count value\n"
            "* if neither /g modifier nor --count argument is passed, assume that --count is equal 1\n"
            "* if only --count is given, this value is used\n"
            "* if --eval-replace is given, --replace must be valid Python code, where can be used m variable."
                "m holds MatchObject instance (see: http://http://docs.python.org/2/library/re.html#match-objects, "
                "for example:\n"
            "    --eval-replace --replace 'm.group (1).lower ()'\n"
            "* regular expressions with non linear search read whole file to yours computer memory - if file size is "
                "bigger then you have memory in your computer, it fails\n"
            "* parsing expression passed to --pattern_and_replace argument is very simple - if you use / as delimiter, "
                "then in your expression can\'t be used this character anymore. If you need to use same character as "
                "delimiter and in expression, then better use --pattern and --replace argument\n"
#             "* "
            "\n"
            "Security notes:\n"
            "* be carefull with --eval-replace argument. When it's given, value passed to --replace is eval-ed, so any not safe code will be executed!\n"
            "\n"
            "Author:\n"
            "Marcin Sztolcman <marcin@urzenia.net> // http://urzenia.net\n"
            "\n"
            "HomePage:\n"
            "https://github.com/mysz/subst/"
        ),
    )

    p.add_argument ('-p', '--pattern', type=str, help='pattern to replace for. Supersede --pattern_and_replace. Required if --replace is specified.')
    p.add_argument ('-r', '--replace', type=str, help='replacement. Supersede --pattern_and_replace. Required if --pattern is specified.')
    p.add_argument ('--eval-replace', dest='eval', action='store_true', help='if specified, make eval data from --replace (should be valid Python code). Ignored with --pattern_and_replace argument.')
    p.add_argument ('-t', '--string', type=bool, help='if specified, treats --pattern as string, not as regular expression. Ignored with --pattern_and_replace argument.')
    p.add_argument ('-s', '--pattern_and_replace', metavar='s/PAT/REP/g', type=str, help='pattern and replacement in one: s/pattern/replace/g (pattern is always regular expression, /g is optional and stands for --count=0).')
    p.add_argument ('-c', '--count', type=int, help='make COUNT replacements for every file (0 make unlimited changes, default).')
    p.add_argument ('-l', '--linear', action='store_true', help='apply pattern for every line separately. Without this flag whole file is read into memory.')
    p.add_argument ('-i', '--ignore-case', dest='ignore_case', action='store_true', help='ignore case of characters when matching')
    p.add_argument ('--pattern-dot-all', dest='pattern_dot_all', action='store_true', help='with this flag, dot (.) character in pattern match also new line character (see: http://docs.python.org/2/library/re.html#re.DOTALL).')
    p.add_argument ('--pattern-verbose', dest='pattern_verbose', action='store_true', help='with this flag pattern can be passed as verbose (see: http://docs.python.org/2/library/re.html#re.VERBOSE).')
    p.add_argument ('--pattern-multiline', dest='pattern_multiline', action='store_true', help='with this flag pattern can be passed as multiline (see: http://docs.python.org/2/library/re.html#re.MULTILINE).')

    p.add_argument ('-b', '--no-backup', dest='no_backup', action='store_true', help='disable creating backup of modified files.')
    p.add_argument ('-e', '--backup-extension', dest='ext', default=DEFAULT_BACKUP_EXTENSION, type=str, help='extension for backuped files (ignore if no backup is created), without leading dot. Defaults to: "bak".')
    p.add_argument ('--stdin', action='store_true', help='read data from STDIN (implies --stdout)')
    p.add_argument ('--stdout', action='store_true', help='output data to STDOUT instead of change files in-place (implies --no-backup)')
    p.add_argument ('--verbose', action='store_true', help='show files and how many replacements was done')
    p.add_argument ('--debug', action='store_true', help='show more infos')
    p.add_argument ('-v', '--version', action='store_true', help='show version and exit')
    p.add_argument ('files', nargs='*', type=str, help='file to parse.')

    args = p.parse_args()

    if args.version:
        return args

    if not args.files or args.files[0] == '-':
        args.stdin = True

    if args.stdin:
        args.stdout = True

    if args.stdout:
        args.no_backup = True

    if \
            (args.pattern is None and args.replace is None and args.pattern_and_replace is None) or \
            (args.pattern is None and args.replace is not None) or \
            (args.pattern is not None and args.replace is None):
        p.error ('must be provided --pattern and --replace options, or --pattern_and_replace.')

    try:
        args.ext = get_ext (args)
        args.pattern, args.replace, args.count = prepare_pattern_data (args)
        args.replace = prepare_replacement (args.replace, args.eval)
    except ParserException, e:
        p.error (e)

    return args

def replace_linear (src, dst, pattern, replace, count):
    """ Read data from 'src' line by line, replace some data from
        regular expression in 'pattern' with data in 'replace',
        write it to 'dst', and return quantity of replaces.
    """
    ret = 0
    for line in src:
        if count == 0 or ret < count:
            line, rest_count = pattern.subn (replace, line, max (0, count - ret))
            ret += rest_count
        dst.write (line)
    return ret

def replace_global (src, dst, pattern, replace, count):
    """ Read whole file from 'src', replace some data from
        regular expression in 'pattern' with data in 'replace',
        write it to 'dst', and return quantity of replaces.
    """
    data = src.read ()
    data, ret = pattern.subn (replace, data, count)
    dst.write (data)
    return ret

def main ():
    args = parse_args (sys.argv[1:])

    if args.version:
        show_version ()

    if args.linear:
        replace_func = replace_linear
    else:
        replace_func = replace_global

    if args.stdin:
        replace_func (sys.stdin, sys.stdout, args.pattern, args.replace, args.count)

    else:
        for path in args.files:
            if args.verbose or args.debug:
                debug (path)

            if not os.path.exists (path):
                errmsg ('Path "{0}" doesn\'t exists'.format (path), int (args.verbose or args.debug))
                continue

            if not os.path.isfile (path) or os.path.islink (path):
                errmsg ('Path "{0}" is not a regular file'.format (path), int (args.verbose or args.debug))
                continue

            if not args.no_backup:
                root = os.path.dirname (path)
                backup_path = os.path.join (root, path + args.ext)

                if os.path.exists (backup_path):
                    errmsg ('Backup path: "{0}" for file "{1}" already exists, file omited'.format (backup_path, path), int (args.verbose or args.debug))
                    continue

                try:
                    shutil.copy2 (path, backup_path)
                except shutil.Error, e:
                    errmsg ('Cannot create backup for "{0}": {1}'.format (path, e), int (args.verbose or args.debug))
                    continue
                except IOError, e:
                    errmsg ('Cannot create backup for "{0}": {1}'.format (path, e), int (args.verbose or args.debug))
                    continue

                if args.debug:
                    debug ('created backup file: "{0}"'.format (backup_path), 1)

            if not args.stdout:
                tmp_fh, tmp_path = tempfile.mkstemp ()
                tmp_fh = os.fdopen (tmp_fh, 'w')

                try:
                    shutil.copy2 (path, tmp_path)
                except shutil.Error, e:
                    errmsg ('Cannot create temporary file "{0}" for "{1}": {2}'.format (tmp_path, path, e), int (args.verbose or args.debug))
                    continue
                except IOError, e:
                    errmsg ('Cannot create temporary file "{0}" for "{1}": {2}'.format (tmp_path, path, e), int (args.verbose or args.debug))
                    continue
                else:
                    if args.debug:
                        debug ('created temporary copy: "{0}"'.format (tmp_path), 1)
            else:
                tmp_fh = sys.stdout

            try:
                with open (path, 'r') as fh_src:
                    cnt = replace_func (fh_src, tmp_fh, args.pattern, args.replace, args.count)
                    if args.verbose or args.debug:
                        debug ('{0} replacements'.format (cnt), 1)

                if not args.stdout:
                    os.rename (tmp_path, path)
                    tmp_fh.close ()
            except OSError, e:
                errmsg ('Error replacing "{0}" with "{1}": {2}'.format (path, tmp_path, e), int (args.verbose or args.debug))
                continue
            else:
                if args.debug:
                    debug ('moved temporary file to original', 1)

if __name__ == '__main__':
    main ()
