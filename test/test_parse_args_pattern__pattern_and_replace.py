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


def test_no_s_prefix(argparse_args):
    argparse_args.pattern_and_replace = '/a/b/'

    try:
        subst._parse_args__pattern(argparse_args)
    except subst.ParserException:
        pass
    else:
        pytest.fail('ParserException excepted when "s" prefix is missing')


def test_no_flags(argparse_args):
    argparse_args.pattern_and_replace = 's/a/b/'

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'
    assert pat.flags == re.UNICODE
    assert rep == 'b'
    assert cnt == 1


def test_with_single_flag(argparse_args, fixt_single_flag):
    argparse_args.pattern_and_replace = 's/a/b/' + fixt_single_flag

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'
    assert pat.flags == re.UNICODE | _re_flag(fixt_single_flag)
    assert rep == 'b'
    assert cnt == 1


def test_with_single_flag_and_g_flag(argparse_args, fixt_single_flag):
    argparse_args.pattern_and_replace = 's/a/b/g' + fixt_single_flag

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'
    assert pat.flags == re.UNICODE | _re_flag(fixt_single_flag)
    assert rep == 'b'
    assert cnt == 0


def test_with_two_flags(argparse_args, fixt_two_flags):
    argparse_args.pattern_and_replace = 's/a/b/' + fixt_two_flags

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'

    expected_flags = re.UNICODE
    for flag in fixt_two_flags:
        expected_flags |= _re_flag(flag)
    assert pat.flags == expected_flags
    assert rep == 'b'
    assert cnt == 1


def test_with_two_flags_and_g_flag(argparse_args, fixt_two_flags):
    argparse_args.pattern_and_replace = 's/a/b/g' + fixt_two_flags

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'

    expected_flags = re.UNICODE
    for flag in fixt_two_flags:
        expected_flags |= _re_flag(flag)
    assert pat.flags == expected_flags
    assert rep == 'b'
    assert cnt == 0


def test_with_all_flags(argparse_args, fixt_all_flags):
    argparse_args.pattern_and_replace = 's/a/b/' + fixt_all_flags

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'

    expected_flags = re.UNICODE
    for flag in fixt_all_flags:
        expected_flags |= _re_flag(flag)
    assert pat.flags == expected_flags
    assert rep == 'b'
    assert cnt == 1


def test_with_all_flags_and_g_flag(argparse_args, fixt_all_flags):
    argparse_args.pattern_and_replace = 's/a/b/g' + fixt_all_flags

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'

    expected_flags = re.UNICODE
    for flag in fixt_all_flags:
        expected_flags |= _re_flag(flag)
    assert pat.flags == expected_flags
    assert rep == 'b'
    assert cnt == 0


def test_delim_brackets(argparse_args):
    argparse_args.pattern_and_replace = 's(a)(b)gsx'

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'
    assert pat.flags == re.UNICODE | re.DOTALL | re.VERBOSE
    assert rep == 'b'
    assert cnt == 0

    argparse_args.pattern_and_replace = 's(a)(b)'
    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'
    assert pat.flags == re.UNICODE
    assert rep == 'b'
    assert cnt == 1


def test_delim_square_brackets(argparse_args):
    argparse_args.pattern_and_replace = 's[a][b]gsx'

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'
    assert pat.flags == re.UNICODE | re.DOTALL | re.VERBOSE
    assert rep == 'b'
    assert cnt == 0

    argparse_args.pattern_and_replace = 's[a][b]'
    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'
    assert pat.flags == re.UNICODE
    assert rep == 'b'
    assert cnt == 1


def test_delim_braces(argparse_args):
    argparse_args.pattern_and_replace = 's{a}{b}gsx'

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'
    assert pat.flags == re.UNICODE | re.DOTALL | re.VERBOSE
    assert rep == 'b'
    assert cnt == 0

    argparse_args.pattern_and_replace = 's{a}{b}'
    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'
    assert pat.flags == re.UNICODE
    assert rep == 'b'
    assert cnt == 1


def test_delim_sharp_brackets(argparse_args):
    argparse_args.pattern_and_replace = 's<a><b>gsx'

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'
    assert pat.flags == re.UNICODE | re.DOTALL | re.VERBOSE
    assert rep == 'b'
    assert cnt == 0

    argparse_args.pattern_and_replace = 's<a><b>'
    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'
    assert pat.flags == re.UNICODE
    assert rep == 'b'
    assert cnt == 1


def test_delim_other_char(argparse_args, fixt_printable):
    if fixt_printable in '(){}[]<>':
        return

    pattern1 = 'a' if fixt_printable != 'a' else 'q'
    replacement1 = 'b' if fixt_printable != 'b' else 'w'

    argparse_args.pattern_and_replace = 's' + fixt_printable + pattern1 + fixt_printable + replacement1 + fixt_printable + 'gsx'

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == pattern1
    assert pat.flags == re.UNICODE | re.DOTALL | re.VERBOSE
    assert rep == replacement1
    assert cnt == 0

    argparse_args.pattern_and_replace = 's' + fixt_printable + pattern1 + fixt_printable + replacement1 + fixt_printable

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == pattern1
    assert pat.flags == re.UNICODE
    assert rep == replacement1
    assert cnt == 1


def test_invalid_braces(argparse_args, fixt_opening_brace):
    argparse_args.pattern_and_replace = 's' + fixt_opening_brace + 'a' + fixt_opening_brace + 'b' + fixt_opening_brace + 'gsx'

    try:
        subst._parse_args__pattern(argparse_args)
    except subst.ParserException:
        pass
    else:
        pytest.fail('ParserException excepted for ' + argparse_args.pattern_and_replace)

    argparse_args.pattern_and_replace = 's' + fixt_opening_brace + 'a' + fixt_opening_brace + 'b' + fixt_opening_brace

    try:
        subst._parse_args__pattern(argparse_args)
    except subst.ParserException:
        pass
    else:
        pytest.fail('ParserException excepted for ' + argparse_args.pattern_and_replace)


def test_unknown_flag(argparse_args, fixt_printable):
    if fixt_printable in 'gixsm':
        return

    argparse_args.pattern_and_replace = 's/a/b/' + fixt_printable

    try:
        subst._parse_args__pattern(argparse_args)
    except subst.ParserException:
        pass
    else:
        pytest.fail('ParserException excepted for invalid flag: ' + fixt_printable)


    argparse_args.pattern_and_replace = 's/a/b/gxs' + fixt_printable

    try:
        subst._parse_args__pattern(argparse_args)
    except subst.ParserException:
        pass
    else:
        pytest.fail('ParserException excepted for invalid flag: ' + fixt_printable)


def test_delim_in_pattern(argparse_args):
    argparse_args.pattern_and_replace = 's!a!b!c!'

    try:
        subst._parse_args__pattern(argparse_args)
    except subst.ParserException:
        pass
    else:
        pytest.fail('ParserException excepted for pattern: ' + argparse_args.pattern_and_replace)


@pytest.mark.parametrize('param', ['ignore_case', 'pattern_dot_all', 'pattern_verbose', 'pattern_multiline'])
def test_flags_with_flags_in_params(argparse_args, fixt_two_flags, param):
    argparse_args.pattern_and_replace = 's/a/b/' + fixt_two_flags
    setattr(argparse_args, param, True)

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'

    param_flag = dict(
        ignore_case=re.IGNORECASE,
        pattern_dot_all=re.DOTALL,
        pattern_verbose=re.VERBOSE,
        pattern_multiline=re.MULTILINE
    )[param]
    expected_flags = re.UNICODE | param_flag
    for flag in fixt_two_flags:
        expected_flags |= _re_flag(flag)
    assert pat.flags == expected_flags
    assert rep == 'b'
    assert cnt == 1


@pytest.mark.parametrize('param', ['ignore_case', 'pattern_dot_all', 'pattern_verbose', 'pattern_multiline'])
def test_no_flags_with_flags_in_params(argparse_args, param):
    argparse_args.pattern_and_replace = 's/a/b/'
    setattr(argparse_args, param, True)

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'

    param_flag = dict(
        ignore_case=re.IGNORECASE,
        pattern_dot_all=re.DOTALL,
        pattern_verbose=re.VERBOSE,
        pattern_multiline=re.MULTILINE
    )[param]
    assert pat.flags == re.UNICODE | param_flag
    assert rep == 'b'
    assert cnt == 1


def test_with_count_without_g_flag(argparse_args):
    argparse_args.pattern_and_replace = 's/a/b/'
    argparse_args.count = 3

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'
    assert pat.flags == re.UNICODE
    assert rep == 'b'
    assert cnt == 3


def test_with_count_with_g_flag(argparse_args):
    argparse_args.pattern_and_replace = 's/a/b/g'
    argparse_args.count = 3

    pat, rep, cnt = subst._parse_args__pattern(argparse_args)

    assert isinstance(pat, RE_TYPE)
    assert pat.pattern == 'a'
    assert pat.flags == re.UNICODE
    assert rep == 'b'
    assert cnt == 0

if __name__ == '__main__':
    pytest.main()
