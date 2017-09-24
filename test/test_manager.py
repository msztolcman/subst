# -*- coding: utf-8 -*-

import os.path
import sys

__all__ = ['PLAYGROUND_PATH', 'IS_PY2']

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PLAYGROUND_PATH = os.path.join(os.path.dirname(__file__), 'playground')
IS_PY2 = sys.version_info[0] < 3
