# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from __future__ import (absolute_import, print_function, unicode_literals)
from ..std.sphinx import DEFAULT_HIGHLIGHT_STYLE
from docutils import nodes
from sphinx.writers.text import TextTranslator
import sys

# supported confluence list types
class ConflueceListType(object):
    BULLET = 1
    ENUMERATED = 2

# abstract sphinx translator for sphinxcontrib.confluencebuilder
class ConfluenceTranslator(TextTranslator):
    def __init__(self, document, builder):
        TextTranslator.__init__(self, document, builder)

        if self.builder.config.highlight_language:
            self._highlight = self.builder.config.highlight_language
        else:
            self._highlight = DEFAULT_HIGHLIGHT_STYLE
        self._linenothreshold = sys.maxsize

    def visit_centered(self, node):
        # centered is deprecated; ignore
        # http://www.sphinx-doc.org/en/stable/markup/para.html#directive-centered
        pass

    def depart_centered(self, node):
        pass

    def visit_highlightlang(self, node):
        # update the translator's highlight language from the defined directive
        # http://www.sphinx-doc.org/en/stable/markup/code.html#directive-highlight
        self._highlight = node.get('lang', DEFAULT_HIGHLIGHT_STYLE)
        self._linenothreshold = node.get('linenothreshold', sys.maxsize)
        raise nodes.SkipNode

    def visit_start_of_file(self, node):
        # ignore managing state of inlined documents
        pass

    def depart_start_of_file(self, node):
        pass

    def visit_meta(self, node):
        # always ignore meta nodes as they are html-specific
        # http://docutils.sourceforge.net/docs/ref/rst/directives.html#meta
        raise nodes.SkipNode

    def unknown_visit(self, node):
        raise NotImplementedError('unknown node: ' + node.__class__.__name__)
