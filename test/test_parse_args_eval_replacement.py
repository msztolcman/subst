#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os, os.path
import re
import sys
import types

from pprint import pprint, pformat

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from test_manager import *
import subst

class TestParseArgsEvalReplacement(unittest.TestCase):
    def test_invalid_code_name_error(self):
        code = 'asd'

        result = subst._parse_args__eval_replacement(code)

        self.assertEqual(type(result), types.FunctionType)
        if IS_PY2:
            self.assertRaisesRegexp(TypeError, r'takes exactly 1 argument', result)
        else:
            self.assertRaisesRegexp(TypeError, r'missing 1 required positional argument', result)
        self.assertRaisesRegexp(NameError, r"'asd' is not defined", lambda: result('a'))

    def test_invalid_code_syntax_error(self):
        code = 'in = 3'

        result = subst._parse_args__eval_replacement(code)

        self.assertEqual(type(result), types.FunctionType)
        if IS_PY2:
            self.assertRaisesRegexp(TypeError, r'takes exactly 1 argument', result)
        else:
            self.assertRaisesRegexp(TypeError, r'missing 1 required positional argument', result)
        self.assertRaises(SyntaxError, lambda: result('a'))

    def test_function_simple_match(self):
        code = 'm.group(0)'
        match = re.search(r'(ala)', 'QalaQ')

        result = subst._parse_args__eval_replacement(code)

        self.assertEqual(type(result), types.FunctionType)
        self.assertEqual(result(match), 'ala')

    def test_simple_replace(self):
        code = '""'

        result = subst._parse_args__eval_replacement(code)

        data_in = 'QalaQ'
        data_out = re.sub(r'(ala)', result, data_in)

        self.assertEqual(data_out, 'QQ')

    def test_regexp_replace(self):
        code = 'm.group(0).upper()'

        result = subst._parse_args__eval_replacement(code)

        data_in = 'Qala has catQ'
        data_out = re.sub(r'([am])', result, data_in)

        self.assertEqual(data_out, 'QAlA hAs cAtQ')

    def test_builtins_available(self):
        code = 'str(pow(int(m.group(0)), 2))'

        result = subst._parse_args__eval_replacement(code)

        data_in = 'Qala has 2 cats i 4 dogsQ'
        data_out = re.sub(r'(\d)', result, data_in)

        self.assertEqual(data_out, 'Qala has 4 cats i 16 dogsQ')

    def test_three_groups(self):
        code = 'str(sum(map(int, m.groups()))) + " animals"'

        result = subst._parse_args__eval_replacement(code)

        data_in = 'Qala has 2 cats, 4 dogs i 7 chickensQ'
        data_out = re.sub(r'(\d).*(\d).*(\d).*Q$', result, data_in)

        self.assertEqual(data_out, 'Qala has 13 animals')

if __name__ == '__main__':
    unittest.main()
