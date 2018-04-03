# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from __future__ import (absolute_import, print_function, unicode_literals)
from .logger import ConfluenceLogger
from .translator.wiki import ConfluenceWikiTranslator
from docutils import writers

class ConfluenceWriter(writers.Writer):
    supported = ('text',)
    settings_spec = ('No options here.', '', ())
    settings_defaults = {}

    def __init__(self, builder):
        writers.Writer.__init__(self)
        self.builder = builder
        self.output = None

    def translate(self):
        visitor = ConfluenceWikiTranslator(self.document, self.builder)
        self.document.walkabout(visitor)
        if hasattr(visitor, 'body'):
            self.output = visitor.body
