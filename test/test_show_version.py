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

class TestShowVersion(unittest.TestCase):
    def test(self):
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        self.assertRaises(SystemExit, subst.show_version)

        data = sys.stdout.getvalue()
        sys.stdout = old_stdout

        self.assertRegexpMatches(data, ': version %s' % re.escape(subst.__version__))
