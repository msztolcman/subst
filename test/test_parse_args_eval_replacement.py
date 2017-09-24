#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import re
import types

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import pytest
from .test_manager import *
import subst


def test_invalid_code_name_error():
    code = 'asd'

    result = subst._parse_args__eval_replacement(code)

    assert type(result) is types.FunctionType
    try:
        result()
    except TypeError as exc:
        if IS_PY2:
            assert re.search(r'takes exactly 1 argument', str(exc))
        else:
            assert re.search(r'missing 1 required positional argument', str(exc))

    try:
        result('a')
    except NameError as exc:
        assert re.search(r"'asd' is not defined", str(exc))


def test_invalid_code_syntax_error():
    code = 'in = 3'

    result = subst._parse_args__eval_replacement(code)

    assert type(result) is types.FunctionType

    try:
        result()
    except TypeError as exc:
        if IS_PY2:
            assert re.search(r'takes exactly 1 argument', str(exc))
        else:
            assert re.search(r'missing 1 required positional argument', str(exc))

    try:
        result('a')
    except SyntaxError:
        pass


def test_function_simple_match():
    code = 'm.group(0)'
    match = re.search(r'(ala)', 'QalaQ')

    result = subst._parse_args__eval_replacement(code)

    assert type(result) is types.FunctionType
    assert result(match) == 'ala'


def test_simple_replace():
    code = '""'

    result = subst._parse_args__eval_replacement(code)

    data_in = 'QalaQ'
    data_out = re.sub(r'(ala)', result, data_in)

    assert data_out == 'QQ'


def test_regexp_replace():
    code = 'm.group(0).upper()'

    result = subst._parse_args__eval_replacement(code)

    data_in = 'Qala has catQ'
    data_out = re.sub(r'([am])', result, data_in)

    assert data_out == 'QAlA hAs cAtQ'


def test_builtins_available():
    code = 'str(pow(int(m.group(0)), 2))'

    result = subst._parse_args__eval_replacement(code)

    data_in = 'Qala has 2 cats i 4 dogsQ'
    data_out = re.sub(r'(\d)', result, data_in)

    assert data_out == 'Qala has 4 cats i 16 dogsQ'


def test_three_groups():
    code = 'str(sum(map(int, m.groups()))) + " animals"'

    result = subst._parse_args__eval_replacement(code)

    data_in = 'Qala has 2 cats, 4 dogs i 7 chickensQ'
    data_out = re.sub(r'(\d).*(\d).*(\d).*Q$', result, data_in)

    assert data_out == 'Qala has 13 animals'


if __name__ == '__main__':
    pytest.main()
