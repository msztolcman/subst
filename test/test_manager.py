#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os, os.path
import sys
import re
from pprint import pprint, pformat

__all__ = ['PLAYGROUND_PATH', 'IS_PY2', 'unittest']

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PLAYGROUND_PATH = os.path.join(os.path.dirname(__file__), 'playground')
IS_PY2 = sys.version_info[0] < 3

if IS_PY2 and sys.version_info[1] < 7:
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
        class Fail(unittest.TestCase):
            def test_fail(self):
                self.fail('Need unittest2 module for python older then 2.7!')
else:
    import unittest

