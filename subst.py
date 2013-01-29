#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os, os.path
import sys
import re
import shutil
import tempfile
from pprint import pprint, pformat

import argparse

DEFAULT_BACKUP_EXTENSION = 'bak'

class ParserException (Exception): pass
class ReplaceException (Exception): pass

def errmsg (msg):
    print (msg, file=sys.stderr)

def msg (msg):
    print (msg)

def debug (msg):
    print (msg, file=sys.stderr)

def get_ext (args):
    if args.no_backup:
        return ''

    if args.ext is None or len (args.ext) == 0:
        return '.' + DEFAULT_BACKUP_EXTENSION

    return '.' + args.ext

def prepare_replacement (r, to_eval=False):
    if not to_eval:
        return r

    def repl (m):
        return eval (r, { '__builtins__': __builtins__ }, { 'm': m })

    return repl

def prepare_pattern_data (args):
    if args.pattern is not None and args.replace is not None:
        if args.string:
            pattern = re.escape (args.pattern)
        else:
            pattern = args.pattern

        return re.compile (pattern), args.replace, args.count

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
                count = 1

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

        return re.compile (pattern), replace, count
    else:
        raise ParserException ('Bad pattern specified: {0}'.format (args.pattern_and_replace))

def parse_args (args):
    p = argparse.ArgumentParser (
        description='Replace PATTERN with REPLACE in many files',
        epilog='',
    )
    p.add_argument ('-p', '--pattern', type=str, help='pattern to replace for. Supersede --pattern_and_replace. Required if --replace is specified.')
    p.add_argument ('-r', '--replace', type=str, help='replacement. Supersede --pattern_and_replace. Required if --pattern is specified.')
    p.add_argument ('-t', '--string', type=bool, help='if specified, treats --pattern as string, not as regular expression. Works only with --pattern switch.')
    p.add_argument ('--eval-replace', dest='eval', action='store_true', help='if specified, make eval data from --replace (should be valid Python code). Ignored with --pattern_and_replace argument.')
    p.add_argument ('-s', '--pattern_and_replace', metavar='s/PAT/REP/g', type=str, help='pattern and replacement in one: s/pattern/replace/g (pattern is always regular expression, /g is optional and stands for --count=0).')
    p.add_argument ('-c', '--count', default=0, type=int, help='make COUNT replacements for every file (0 make unlimited changes, default).')
    p.add_argument ('-l', '--linear', action='store_true', help='apply pattern for every line separately. Without this flag whole file is read into memory.')
    p.add_argument ('-b', '--no-backup', dest='no_backup', action='store_true', help='disable creating backup of modified files.')
    p.add_argument ('-e', '--backup-extension', dest='ext', default=DEFAULT_BACKUP_EXTENSION, type=str, help='extension for backuped files (ignore if no backup is created), without leading dot. Defaults to: "bak".')
    p.add_argument ('--verbose', action='store_true', help='works in verbose mode.')
    p.add_argument ('files', nargs='+', type=str, help='file to parse.')

    args = p.parse_args()

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

def replace_linear (path, dst, pattern, replace, count):
    ret = 0
    with open (path, 'r') as fh_src:
        with open (dst, 'w') as fh_dst:
            for line in fh_src:
                if count == 0 or ret < count:
                    line, rest_count = pattern.subn (replace, line, max (0, count - ret))
                    ret += rest_count
                fh_dst.write (line)
    return ret

def replace_global (path, dst, pattern, replace, count):
    with open (path, 'r') as fh_src:
        with open (dst, 'w') as fh_dst:
            data = fh_src.read ()
            data, ret = pattern.subn (replace, data, count)
            fh_dst.write (data)

    return ret

def main ():
    args = parse_args (sys.argv[1:])

    if args.linear:
        replace_func = replace_linear
    else:
        replace_func = replace_global

    for path in args.files:
        if not os.path.exists (path):
            errmsg ('Path "{0}" doesn\'t exists'.format (path))
            continue

        if not os.path.isfile (path) or os.path.islink (path):
            errmsg ('Path "{0}" is not a regular file'.format (path))
            continue

        if not args.no_backup:
            root = os.path.dirname (path)
            backup_path = os.path.join (root, path + args.ext)

            if os.path.exists (backup_path):
                errmsg ('Backup path: "{0}" for file "{1}" already exists, file omited'.format (backup_path, path))
                continue

            try:
                shutil.copy2 (path, backup_path)
            except shutil.Error, e:
                errmsg ('Cannot create backup for "{0}": {1}'.format (path, e))
                continue
            except IOError, e:
                errmsg ('Cannot create backup for "{0}": {1}'.format (path, e))
                continue

            if args.verbose:
                debug ('Created backup: "{0}" -> "{1}"'.format (path, backup_path))

        tmp_fh, tmp_path = tempfile.mkstemp ()
        os.close (tmp_fh)

        try:
            shutil.copy2 (path, tmp_path)
        except shutil.Error, e:
            errmsg ('Cannot create temporary file "{0}" for "{1}": {2}'.format (tmp_path, path, e))
            continue
        except IOError, e:
            errmsg ('Cannot create temporary file "{0}" for "{1}": {2}'.format (tmp_path, path, e))
            continue
        else:
            if args.verbose:
                debug ('Created temporary copy: "{0}" -> "{1}"'.format (path, tmp_path))

        try:
            cnt = replace_func (path, tmp_path, args.pattern, args.replace, args.count)
            if args.verbose:
                debug ('Made {0} replacements in "{1}" ("{2}")'.format (cnt, path, tmp_path))

            os.rename (tmp_path, path)
        except ReplaceException, e:
            errmsg ('Error processing "{0}" ("{1}"): {2}'.format (path, tmp_path, e))
            continue
        except OSError, e:
            errmsg ('Error replacing "{0}" with "{1}": {2}'.format (path, tmp_path, e))
            continue
        else:
            if args.verbose:
                debug ('Moved temporary file to destination: "{0}" -> "{1}"'.format (tmp_path, path))

if __name__ == '__main__':
    main ()
