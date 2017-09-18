#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os, os.path
import sys
import re
from pprint import pprint, pformat

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from test_manager import *
import subst

class MockArgParse(object):
    def __init__(self):
        self.no_backup = False
        self.ext = None

class TestParseArgsGetExt(unittest.TestCase):
    def test_simple(self):
        args = MockArgParse()

        result = subst._parse_args__get_backup_file_ext(args)

        self.assertEqual(result, '.' + subst.DEFAULT_BACKUP_EXTENSION)

    def test_no_backup(self):
        args = MockArgParse()
        args.no_backup = True

        result = subst._parse_args__get_backup_file_ext(args)

        self.assertEqual(result, '')

    def test_given_ext_no_dot(self):
        args = MockArgParse()
        args.ext = 'jpg'

        result = subst._parse_args__get_backup_file_ext(args)

        self.assertEqual(result, '.' + args.ext)

    def test_given_ext_with_dot(self):
        args = MockArgParse()
        args.ext = '.jpg'

        result = subst._parse_args__get_backup_file_ext(args)

        self.assertEqual(result, '.' + args.ext)

    def test_given_ext_with_no_backup(self):
        args = MockArgParse()
        args.ext = 'jpg'
        args.no_backup = True

        result = subst._parse_args__get_backup_file_ext(args)

        self.assertEqual(result, '')

if __name__ == '__main__':
    unittest.main()
