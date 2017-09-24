#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import itertools
import re
import string
import types

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import pytest
from .test_manager import *
import subst

RE_TYPE = type(re.compile(r''))

@pytest.fixture()
def argparse_args():
    class NS: pass

    args = NS()
    args.ignore_case = False
    args.pattern_dot_all = False
    args.pattern_verbose = False
    args.pattern_multiline = False
    args.pattern = None
    args.replace = None
    args.pattern_and_replace = ''
    args.count = None
    args.string = False

    return args


def _re_flag(flag):
    if flag == 'i':
        return re.IGNORECASE
    if flag == 'x':
        return re.VERBOSE
    if flag == 's':
        return re.DOTALL
    if flag == 'm':
        return re.MULTILINE


@pytest.fixture(params='ixsm')
def fixt_single_flag(request):
    return request.param


@pytest.fixture(params=itertools.permutations('ixsm', 2))
def fixt_two_flags(request):
    return ''.join(request.param)


@pytest.fixture(params=itertools.permutations('ixsm'))
def fixt_all_flags(request):
    return ''.join(request.param)


@pytest.fixture(params=string.printable)
def fixt_printable(request):
    return request.param


@pytest.fixture(params='([{<')
def fixt_opening_brace(request):
    return request.param


def test_no_pattern_at_all(argparse_args):
    try:
        subst._parse_args__pattern(argparse_args)
    except subst.ParserException:
        pass
    else:
        pytest.fail('ParserException excepted when no pattern specified')


def test_no_pattern_specified(argparse_args):
    argparse_args.replace = 's'

    try:
        subst._parse_args__pattern(argparse_args)
    except subst.ParserException:
        pass
    else:
        pytest.fail('ParserException excepted when no pattern specified')


def test_no_replace_specified(argparse_args):
    argparse_args.pattern = 's'

    try:
        subst._parse_args__pattern(argparse_args)
    except subst.ParserException:
        pass
    else:
        pytest.fail('ParserException excepted when no replace    specified')


def test_with_no_flags(argparse_args):
    argparse_args.pattern = 'a.b'
    argparse_args.replace = 'c'

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == r'a.b'
    assert pat.flags == re.UNICODE
    assert rep == 'c'
    assert cnt == 0


@pytest.mark.parametrize('param1', ['ignore_case', 'pattern_dot_all', 'pattern_verbose', 'pattern_multiline'])
@pytest.mark.parametrize('param2', ['ignore_case', 'pattern_dot_all', 'pattern_verbose', 'pattern_multiline'])
def test_with_params_flags(argparse_args, param1, param2):
    argparse_args.pattern = 'a'
    argparse_args.replace = 'b'
    setattr(argparse_args, param1, True)
    setattr(argparse_args, param2, True)

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'
    params_mapper = dict(
        ignore_case=re.IGNORECASE,
        pattern_dot_all=re.DOTALL,
        pattern_verbose=re.VERBOSE,
        pattern_multiline=re.MULTILINE
    )
    param1_flag = params_mapper[param1]
    param2_flag = params_mapper[param2]
    assert pat.flags == re.UNICODE | param1_flag | param2_flag
    assert rep == 'b'
    assert cnt == 0


def test_with_string_param(argparse_args):
    argparse_args.pattern = 'a.b'
    argparse_args.replace = 'c'
    argparse_args.string = True

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == r'a\.b'
    assert pat.flags == re.UNICODE
    assert rep == 'c'
    assert cnt == 0

if __name__ == '__main__':
    pytest.main()
