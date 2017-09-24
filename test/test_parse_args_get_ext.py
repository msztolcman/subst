#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import re

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import pytest
from .test_manager import *
import subst


class MockArgParse(object):
    def __init__(self):
        self.no_backup = False
        self.ext = None


def test_simple():
    args = MockArgParse()

    result = subst._parse_args__get_backup_file_ext(args)

    assert result == '.' + subst.DEFAULT_BACKUP_EXTENSION


def test_no_backup():
    args = MockArgParse()
    args.no_backup = True

    result = subst._parse_args__get_backup_file_ext(args)

    assert result == ''


def test_given_ext_no_dot():
    args = MockArgParse()
    args.ext = 'jpg'

    result = subst._parse_args__get_backup_file_ext(args)

    assert result == '.' + args.ext


def test_given_ext_with_dot():
    args = MockArgParse()
    args.ext = '.jpg'

    result = subst._parse_args__get_backup_file_ext(args)

    assert result == '.' + args.ext


def test_given_ext_with_no_backup():
    args = MockArgParse()
    args.ext = 'jpg'
    args.no_backup = True

    result = subst._parse_args__get_backup_file_ext(args)

    assert result == ''


if __name__ == '__main__':
    pytest.main()
