# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.translator.shared
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2016-2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from __future__ import (absolute_import, print_function, unicode_literals)
from sphinx.writers.text import TextTranslator

LANG_MAP = {
    'c': 'cpp',
    'py': 'python'
}

class ConflueceListType(object):
    BULLET = 1
    ENUMERATED = 2

class ConfluenceTranslator(TextTranslator):
    def __init__(self, document, builder):
        TextTranslator.__init__(self, document, builder)
