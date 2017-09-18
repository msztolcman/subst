#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" subst - Replace PATTERN with REPLACE in many files.
    http://msztolcman.github.io/subst
    Author: Marcin Sztolcman (marcin@urzenia.net)

    Get help with: subst --help
    Information about version: subst --version
"""

from __future__ import print_function, unicode_literals, division

import argparse
import codecs
import functools
import glob
import os
import os.path
import re
import shutil
import sys
import tempfile
import textwrap
import unicodedata

__version__ = '0.4.0'

IS_PY2 = sys.version_info[0] < 3
FILESYSTEM_ENCODING = sys.getfilesystemencoding()
FILE_ENCODING = sys.getdefaultencoding()
INPUT_ENCODING = sys.getdefaultencoding()
DEFAULT_BACKUP_EXTENSION = 'bak'


file_opener = functools.partial(open, newline='') if not IS_PY2 else open


class SubstException(Exception):
    """ Exception raised when there is some error.
    """


class ParserException(SubstException):
    """ Exception raised when pattern given by user has errors.
    """


def u(string, encoding='utf-8'):
    """ Wrapper to decode string into unicode.
        Converts only when `string` is type of `str`, and in python2.
        Thanks to this there is possible single codebase between PY2 and PY3.
    """
    if not IS_PY2:
        if isinstance(string, bytes):
            return str(string, encoding=encoding)
    else:
        if isinstance(string, str):
            return string.decode(encoding)
        elif not isinstance(string, unicode):
            return unicode(string)

    return string


def err(*args, **kwargs):
    """
    Display error message.

    It's a wrapper for utils.disp, with additions:
        * file - if not specified, use sys.stderr
        * exit_code - if specified, calls sys.exit with given code. If None, do not exit.

    :param args:
    :param kwargs:
    :return:
    """
    args = list(args)
    args.insert(0, 'ERROR:')

    if not kwargs.get('file'):
        kwargs['file'] = sys.stderr

    disp(*args, **kwargs)

    if kwargs.get('exit_code', None) is not None:
        sys.exit(kwargs['exit_code'])


def disp(*args, **kwargs):
    """ Print data in safe way.

        First, try to encode whole data to utf-8. If printing fails, try to encode to
        sys.stdout.encoding or sys.getdefaultencoding(). In last step, encode to 'ascii'
        with replacing unconvertable characters.
    """

    indent = (' ' * kwargs.get('indent', 0) * 4)
    if indent:
        args = list(args)
        args.insert(0, indent[:-1])

    try:
        if IS_PY2:
            args = [part.encode('utf-8') for part in args]
        print(*args, sep=kwargs.get('sep'), end=kwargs.get('end'), file=kwargs.get('file'))
    except UnicodeEncodeError:
        try:
            encoding = sys.stdout.encoding or sys.getdefaultencoding()
            args = [part.encode(encoding) for part in args]
            print(*args, sep=kwargs.get('sep'), end=kwargs.get('end'), file=kwargs.get('file'))
        except UnicodeEncodeError:
            args = [part.encode('ascii', 'replace') for part in args]
            print(*args, sep=kwargs.get('sep'), end=kwargs.get('end'), file=kwargs.get('file'))


def debug(message, **kwargs):
    """ Display debug message.

        Prints always to stderr.
    """

    kwargs['file'] = sys.stderr
    disp(message, **kwargs)


def _parse_args__get_backup_file_ext(args):
    """ Find extension for backup files.

        Extension in args is supposed to not have leading dot.
    """
    if args.no_backup:
        return ''

    if not args.ext:
        return '.' + DEFAULT_BACKUP_EXTENSION

    return '.' + args.ext


def _parse_args__eval_replacement(repl):
    """ Compile replace argument as valid Python code and return
        function which can be passed to re.sub or re.subn functions.
    """
    # pylint: disable=missing-docstring
    def _(match):
        # pylint: disable=eval-used
        return eval(repl, {'__builtins__': __builtins__}, {'m': match})

    return _


def _parse_args__parse_pattern(pat):
    """
    Split pattern into search, replacement and flags.
    :param pat:
    :return:
    """

    def _parse_args__split_bracketed_pattern(delim, pattern):
        """
        Helper for parsing arguments: search user-given pattern for delim
        and extract flags, replacement and specific pattern from it
        :param delim:
        :param pattern:
        :return:
        """
        pattern, replace = pattern[1:].split(delim[::-1], 1)
        if replace.endswith(delim[1]):
            flags = ''
        else:
            replace, flags = replace.rsplit(delim[1], 1)

        return pattern, replace, flags

    if pat.startswith('('):
        pattern, replace, flags = _parse_args__split_bracketed_pattern('()', pat)
    elif pat.startswith('{'):
        pattern, replace, flags = _parse_args__split_bracketed_pattern('{}', pat)
    elif pat.startswith('['):
        pattern, replace, flags = _parse_args__split_bracketed_pattern('[]', pat)
    elif pat.startswith('<'):
        pattern, replace, flags = _parse_args__split_bracketed_pattern('<>', pat)
    else:
        delim, pat = pat[0], pat[1:]
        pattern, replace, flags = pat.split(delim, 2)

    return pattern, replace, flags


# pylint: disable=too-many-branches
def _parse_args__pattern(args):
    """ Read arguments from argparse.ArgumentParser instance, and
        parse it to find correct values for arguments:
            * pattern
            * replace
            * count
        If is provided --pattern-and-replace argument, then parse
        it and return data from it.

        In other case just return data from argparse.ArgumentParser
        instance.

        Reads also string argument, and apply it to pattern.

        Returned pattern is compiled (see: re.compile).
    """

    re_flags = re.UNICODE

    if args.pattern is not None and args.replace is not None:
        if args.string:
            pattern = re.escape(args.pattern)
        else:
            pattern = args.pattern

        return re.compile(pattern, re_flags), args.replace, args.count or 0

    elif args.pattern_and_replace is not None:
        pat = args.pattern_and_replace

        try:
            # pattern must begin with 's'
            if not pat.startswith('s'):
                raise ParserException('Bad pattern specified: %s' % args.pattern_and_replace)
            pat = pat[1:]

            pattern, replace, flags = _parse_args__parse_pattern(pat)

            if 'g' in flags:
                count = 0
            elif args.count is not None:
                count = args.count
            else:
                count = 1

            if 'i' in flags:
                re_flags |= re.IGNORECASE
            if 'x' in flags:
                re_flags |= re.VERBOSE
            if 's' in flags:
                re_flags |= re.DOTALL
            if 'm' in flags:
                re_flags |= re.MULTILINE

        except ValueError:
            raise ParserException('Bad pattern specified: %s' % args.pattern_and_replace)

        if args.ignore_case:
            re_flags |= re.IGNORECASE

        if args.pattern_dot_all:
            re_flags |= re.DOTALL

        if args.pattern_verbose:
            re_flags |= re.VERBOSE

        if args.pattern_multiline:
            re_flags |= re.MULTILINE

        return re.compile(pattern, re_flags), replace, count
    else:
        raise ParserException('Bad pattern specified: %s' % args.pattern_and_replace)


def _parse_args__expand_wildcards(paths):
    """
    Expand wildcards in given paths
    :param paths: 
    :return: 
    """
    _paths = []
    for path in paths:
        _paths.extend(glob.glob(path))

    return _paths


def wrap_text(txt):
    """ Make custom wrapper for passed text.

        Splits given text for lines, and for every line apply custom
        textwrap.TextWrapper settings, then return reformatted string.
    """
    _wrap = textwrap.TextWrapper(
        width=72,
        expand_tabs=True,
        replace_whitespace=False,
        drop_whitespace=True,
        subsequent_indent='  ',
    )
    txt = [_wrap.fill(line) for line in txt.splitlines()]
    return os.linesep.join(txt)


# pylint: disable=too-many-branches,too-many-statements
def parse_args(args):
    """ Parse arguments passed to script, validate it, compile if needed and return.
    """

    # pylint: disable=global-statement
    global INPUT_ENCODING, FILE_ENCODING, FILESYSTEM_ENCODING

    args_description = 'Replace PATTERN with REPLACE in many files.'
    # pylint: disable=invalid-name
    p = argparse.ArgumentParser(
        description=args_description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=wrap_text(textwrap.dedent("""\
            Miscellaneous notes:
            * regular expressions engine used here is PCRE, dialect from Python
            * is required to pass either --pattern and -replace, or --pattern-and-replace argument
            * if pattern passed to --pattern-and-replace has /g modifier, it overwrites --count value
            * if neither /g modifier nor --count argument is passed, assume that --count is equal 1
            * if only --count is given, this value is used
            * if --eval-replace is given, --replace must be valid Python code, where can be used m variable. m holds MatchObject instance (see: https://docs.python.org/3/library/re.html#match-objects, for example:
                --eval-replace --replace 'm.group(1).lower()'
            * regular expressions with non linear search read whole file to yours computer memory - if file size is bigger then you have memory in your computer, it fails
            * parsing expression passed to --pattern-and-replace argument is very simple - if you use / as delimiter, then in your expression can't be used this character anymore. If you need to use same character as delimiter and in expression, then better use --pattern and --replace arguments
            * you can test exit code to verify there was made any changes (exit code = 0) or not (exit code = 1)

            Security notes:
            * be careful with --eval-replace argument. When it's given, value passed to --replace is eval-ed, so any unsafe code will be executed!

            Author:
            Marcin Sztolcman <marcin@urzenia.net> // http://urzenia.net

            HomePage:
            http://msztolcman.github.io/subst/"""
        ))
    )

    p.add_argument('-p', '--pattern', type=str,
                   help='pattern to replace for. Supersede --pattern-and-replace. Required if --replace is specified.')
    p.add_argument('-r', '--replace', type=str,
                   help='replacement. Supersede --pattern-and-replace. Required if --pattern is specified.')
    p.add_argument('--eval-replace', dest='eval', action='store_true',
                   help='if specified, make eval data from --replace(should be valid Python code). Ignored with '
                   '--pattern-and-replace argument.')
    p.add_argument('-t', '--string', action='store_true',
                   help='if specified, treats --pattern as string, not as regular expression. Ignored with '
                   '--pattern-and-replace argument.')
    p.add_argument('-s', '--pattern-and-replace', '--pattern-and-replace', metavar='"s/PAT/REP/gixsm"', type=str,
                   help='pattern and replacement in one: s/pattern/replace/g(pattern is always regular expression, /g '
                   'is optional and stands for --count=0, /i == --ignore-case, /s == --pattern-dot-all, /m == --pattern-multiline).')
    p.add_argument('-c', '--count', type=int,
                   help='make COUNT replacements for every file (0 makes unlimited changes, default).')
    p.add_argument('-l', '--linear', action='store_true',
                   help='apply pattern for every line separately. Without this flag whole file is read into memory.')
    p.add_argument('-i', '--ignore-case', dest='ignore_case', action='store_true',
                   help='ignore case of characters when matching')
    p.add_argument('--pattern-dot-all', dest='pattern_dot_all', action='store_true',
                   help='with this flag, dot(.) character in pattern match also new line character (see: '
                   'https://docs.python.org/3/library/re.html#re.DOTALL).')
    p.add_argument('--pattern-verbose', dest='pattern_verbose', action='store_true',
                   help='with this flag pattern can be passed as verbose(see: https://docs.python.org/3/library/re.html#re.VERBOSE).')
    p.add_argument('--pattern-multiline', dest='pattern_multiline', action='store_true',
                   help='with this flag pattern can be passed as multiline(see: https://docs.python.org/3/library/re.html#re.MULTILINE).')
    p.add_argument('-u', '--utf8', action='store_true',
                   help='Use UTF-8 in --encoding-input, --encoding-file and --encoding-filesystem')
    p.add_argument('--encoding-input', type=str, default=INPUT_ENCODING,
                   help='set encoding for parameters like --pattern etc (default for your system: %s)' % INPUT_ENCODING)
    p.add_argument('--encoding-file', type=str, default=FILE_ENCODING,
                   help='set encoding for content of processed files (default for your system: %s)' % FILE_ENCODING)
    p.add_argument('--encoding-filesystem', type=str, default=FILESYSTEM_ENCODING,
                   help='set encoding for paths and filenames (default for your system: %s)' % FILESYSTEM_ENCODING)
    p.add_argument('-b', '--no-backup', dest='no_backup', action='store_true',
                   help='don\'t create backup of modified files.')
    p.add_argument('-e', '--backup-extension', dest='ext', default=DEFAULT_BACKUP_EXTENSION, type=str,
                   help='extension for backup files(ignore if no backup is created), without leading dot. Defaults to: "bak".')
    p.add_argument('-W', '--expand-wildcards', action='store_true',
                   help='expand wildcards (see: https://docs.python.org/3/library/glob.html) in paths')
    p.add_argument('--stdin', action='store_true',
                   help='read data from STDIN(implies --stdout)')
    p.add_argument('--stdout', action='store_true',
                   help='output data to STDOUT instead of change files in-place(implies --no-backup)')
    p.add_argument('--verbose', action='store_true',
                   help='show files and how many replacements was done and short summary')
    p.add_argument('--debug', action='store_true',
                   help='show more informations')
    p.add_argument('-v', '--version', action='version',
        version="%s %s\n%s" % (os.path.basename(sys.argv[0]), __version__, args_description))
    p.add_argument('files', nargs='*', type=str,
                   help='files to parse')

    args = p.parse_args(args)

    if args.utf8:
        INPUT_ENCODING = FILE_ENCODING = FILESYSTEM_ENCODING = 'utf8'
    else:
        INPUT_ENCODING = args.encoding_input
        FILE_ENCODING = args.encoding_file
        FILESYSTEM_ENCODING = args.encoding_filesystem

    try:
        codecs.lookup(INPUT_ENCODING)
        codecs.lookup(FILE_ENCODING)
        codecs.lookup(FILESYSTEM_ENCODING)
    except LookupError as exc:
        p.error(exc)

    if not args.files:
        args.stdin = True
    else:
        if args.files[0] == '-':
            args.stdin = True
        else:
            args.files = [u(path, FILESYSTEM_ENCODING) for path in args.files]
            if args.expand_wildcards:
                args.files = _parse_args__expand_wildcards(args.files)

    if args.stdin:
        args.stdout = True

    if args.stdout:
        args.no_backup = True

    if \
            (args.pattern is None and args.replace is None and args.pattern_and_replace is None) or \
            (args.pattern is None and args.replace is not None) or \
            (args.pattern is not None and args.replace is None):
        p.error('must be provided --pattern and --replace options, or --pattern-and-replace.')

    if args.pattern:
        args.pattern = u(args.pattern, INPUT_ENCODING)
    if args.replace:
        args.replace = u(args.replace, INPUT_ENCODING)
    if args.pattern_and_replace:
        args.pattern_and_replace = u(args.pattern_and_replace, INPUT_ENCODING)

    try:
        args.ext = _parse_args__get_backup_file_ext(args)
        args.pattern, args.replace, args.count = _parse_args__pattern(args)
        if args.eval:
            args.replace = _parse_args__eval_replacement(args.replace)
    except ParserException as ex:
        p.error(ex)

    return args


def replace_linear(src, dst, pattern, replace, count):
    """ Read data from 'src' line by line, replace some data from
        regular expression in 'pattern' with data in 'replace',
        write it to 'dst', and return quantity of replaces.
    """
    ret = 0
    for line in src:
        try:
            line = u(line, FILE_ENCODING)
        except UnicodeDecodeError:
            raise SubstException("Cannot determine encoding of input data, please use --encoding-file option")

        if count == 0 or ret < count:
            line, rest_count = pattern.subn(replace, line, max(0, count - ret))
            ret += rest_count

        if IS_PY2:
            line = line.encode(FILE_ENCODING)

        dst.write(line)
    return ret


def replace_global(src, dst, pattern, replace, count):
    """ Read whole file from 'src', replace some data from
        regular expression in 'pattern' with data in 'replace',
        write it to 'dst', and return quantity of replaces.
    """
    data = src.read()
    try:
        data = u(data, FILE_ENCODING)
    except UnicodeDecodeError:
        raise SubstException("Cannot determine encoding of input data, please use --encoding-file option")

    data, ret = pattern.subn(replace, data, count)

    if IS_PY2:
        data = data.encode(FILE_ENCODING)

    dst.write(data)
    return ret


def _process_file__make_backup(path, backup_ext):
    """ Create backup of file: copy it with new extension.

        Returns path to backup file.
    """

    root = os.path.dirname(path)
    backup_path = os.path.join(root, path + backup_ext)

    if os.path.exists(backup_path):
        raise SubstException('Backup path: "%s" for file "%s" already exists, file skipped' % (backup_path, path))

    try:
        shutil.copy2(path, backup_path)
    except (shutil.Error, IOError) as ex:
        raise SubstException('Cannot create backup for "%s": %s' % (path, ex))

    return backup_path


def _process_file__handle(src_path, dst_fh, cfg, replace_func):
    """ Read data from `src_path`, replace data with `replace_func` and
        save it to `dst_fh`.
    """

    with file_opener(src_path, 'r') as fh_src:
        cnt = replace_func(fh_src, dst_fh, cfg.pattern, cfg.replace, cfg.count)
        if cfg.verbose or cfg.debug:
            debug('%s replacement%s' % (cnt, '' if cnt == 1 else 's'), indent=1)

    return cnt


def _process_file__regular(src_path, cfg, replace_func):
    """ Read data from `src_path`, replace data with `replace_func` and
        save it.

        It's safe operation - first save data to temporary file, and then try to rename
        new file to old one.
    """

    tmp_fh, tmp_path = tempfile.mkstemp()
    tmp_fh = os.fdopen(tmp_fh, 'w')

    cnt = _process_file__handle(src_path, tmp_fh, cfg, replace_func)

    try:
        tmp_fh.close()
    # pylint: disable=bare-except
    except:
        pass

    try:
        shutil.move(tmp_path, src_path)
    except OSError as ex:
        raise SubstException('Error replacing "%s" with "%s": %s' % (src_path, tmp_path, ex))
    else:
        if cfg.debug:
            debug('moved temporary file to original', indent=1)

    return cnt


def process_file(path, replace_func, cfg):
    """ Process single file: open, read, make backup and replace data.
    """

    if cfg.verbose or cfg.debug:
        debug(path)

    if not os.path.exists(path):
        raise SubstException('Path "%s" doesn\'t exists' % path)

    if not os.path.isfile(path) or os.path.islink(path):
        raise SubstException('Path "%s" is not a regular file' % path)

    if not cfg.no_backup:
        backup_path = _process_file__make_backup(path, cfg.ext)

        if cfg.debug:
            debug('created backup file: "%s"' % backup_path, indent=1)

    cnt = 0
    try:
        if cfg.stdout:
            cnt = _process_file__handle(path, sys.stdout, cfg, replace_func)
        else:
            cnt = _process_file__regular(path, cfg, replace_func)
    except SubstException as ex:
        err(u(ex))

    return cnt


def main():
    """ Run tool: parse input arguments, read data, replace and save or display.
    """

    try:
        args = parse_args(sys.argv[1:])
    except (UnicodeDecodeError, UnicodeEncodeError):
        err("Cannot determine encoding of input arguments, please use --encoding-input option", exit_code=1)

    if args.linear:
        replace_func = replace_linear
    else:
        replace_func = replace_global

    if args.stdin:
        cnt_changes = replace_func(sys.stdin, sys.stdout, args.pattern, args.replace, args.count)
        cnt_changed_files = 0

    else:
        cnt_changes = cnt_changed_files = 0
        for path in args.files:
            path = u(path, FILESYSTEM_ENCODING)
            path = unicodedata.normalize('NFKC', path)
            path = os.path.expanduser(path)
            path = os.path.abspath(path)

            try:
                cnt_changes_single = process_file(path, replace_func, args)
                if cnt_changes_single > 0:
                    cnt_changes += cnt_changes_single
                    cnt_changed_files += 1
            except SubstException as exc:
                err(u(exc), indent=int(args.verbose or args.debug), exit_code=1)

    if args.verbose:
        debug('There was %d replacement%s in %d file%s.' % (
            cnt_changes, ('' if cnt_changes == 1 else 's'),
            cnt_changed_files, ('' if cnt_changed_files == 1 else 's'),
        ))

    if cnt_changes > 0:
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
