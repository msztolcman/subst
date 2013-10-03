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

class TestMsg(unittest.TestCase):
    def test_simple(self):
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        data_in = "ala ma kota"
        end = "\n"
        subst.msg(data_in)

        data = sys.stdout.getvalue()
        sys.stdout = old_stdout

        self.assertEqual(data, data_in + end)

    def test_indent(self):
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        data_in = "ala ma kota"
        end = "\n"
        indent = 1
        subst.msg(data_in, indent)

        data = sys.stdout.getvalue()
        sys.stdout = old_stdout

        self.assertEqual(data, ' ' * indent * 4 + data_in + end)

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        data_in = "ala ma kota"
        indent = 2
        subst.msg(data_in, indent)

        data = sys.stdout.getvalue()
        sys.stdout = old_stdout

        self.assertEqual(data, ' ' * indent * 4 + data_in + "\n")

    def test_end(self):
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        data_in = "ala ma kota"
        end = "-"
        subst.msg(data_in, end=end)

        data = sys.stdout.getvalue()
        sys.stdout = old_stdout

        self.assertEqual(data, data_in + end)

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        data_in = "ala ma kota"
        end = "__END__"
        subst.msg(data_in, end=end)

        data = sys.stdout.getvalue()
        sys.stdout = old_stdout

        self.assertEqual(data, data_in + end)
