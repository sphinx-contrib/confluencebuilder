# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.translator.shared
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2016-2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from __future__ import (absolute_import, print_function, unicode_literals)
from docutils import nodes
from sphinx.writers.text import TextTranslator

# map of sphinx literal types to confluence code types
#
# This isn't a complete map of support Confluence code types. Unless specified
# here, the default translator pattern will be to directly place a literal's
# explicit language value into a Confluence's code macro language field. This
# map serves as a helper to translate common Sphinx language definitions to
# explicit language types supported by Confluence.
LITERAL2CODE_MAP = {
    'c': 'cpp',
    'py': 'python'
}

# supported confluence list types
class ConflueceListType(object):
    BULLET = 1
    ENUMERATED = 2

# abstract sphinx translator for sphinxcontrib.confluencebuilder
class ConfluenceTranslator(TextTranslator):
    def __init__(self, document, builder):
        TextTranslator.__init__(self, document, builder)

    def visit_centered(self, node):
        # centered is deprecated; ignore
        # http://www.sphinx-doc.org/en/stable/markup/para.html#directive-centered
        pass

    def depart_centered(self, node):
        pass

    def visit_meta(self, node):
        # always ignore meta nodes as they are html-specific
        # http://docutils.sourceforge.net/docs/ref/rst/directives.html#meta
        raise nodes.SkipNode

    def unknown_visit(self, node):
        raise NotImplementedError('unknown node: ' + node.__class__.__name__)
