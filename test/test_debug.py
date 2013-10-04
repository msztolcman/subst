#!/usr/bin/env python -tt
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

class TestErrMsg(unittest.TestCase):
    def test_simple(self):
        old_stderr = sys.stderr
        sys.stderr = StringIO()

        data_in = "ala ma kota"
        end = "\n"
        subst.debug(data_in)

        data = sys.stderr.getvalue()
        sys.stderr = old_stderr

        self.assertEqual(data, data_in + end)

    def test_indent(self):
        old_stderr = sys.stderr
        sys.stderr = StringIO()

        data_in = "ala ma kota"
        end = "\n"
        indent = 1
        subst.debug(data_in, indent)

        data = sys.stderr.getvalue()
        sys.stderr = old_stderr

        self.assertEqual(data, ' ' * indent * 4 + data_in + end)

        old_stderr = sys.stderr
        sys.stderr = StringIO()

        data_in = "ala ma kota"
        indent = 2
        subst.debug(data_in, indent)

        data = sys.stderr.getvalue()
        sys.stderr = old_stderr

        self.assertEqual(data, ' ' * indent * 4 + data_in + "\n")

    def test_end(self):
        old_stderr = sys.stderr
        sys.stderr = StringIO()

        data_in = "ala ma kota"
        end = "-"
        subst.debug(data_in, end=end)

        data = sys.stderr.getvalue()
        sys.stderr = old_stderr

        self.assertEqual(data, data_in + end)

        old_stderr = sys.stderr
        sys.stderr = StringIO()

        data_in = "ala ma kota"
        end = "__END__"
        subst.debug(data_in, end=end)

        data = sys.stderr.getvalue()
        sys.stderr = old_stderr

        self.assertEqual(data, data_in + end)

if __name__ == '__main__':
    unittest.main()
