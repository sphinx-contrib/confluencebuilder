# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from __future__ import unicode_literals
from docutils import nodes
from docutils.nodes import NodeVisitor as BaseTranslator

class ConfluenceTranslator(BaseTranslator):
    """
    confluence extension translator

    Translator instance for the Confluence extension for Sphinx. This
    implementation is responsible for processing individual documents based on
    parsed node entries provided by docutils (used by Sphinx).

    Args:
        document: the document being translated
        builder: the sphinx builder instance
    """
    def __init__(self, document, builder):
        BaseTranslator.__init__(self, document)
        self.builder = builder

        self.body = []
        self.context = []

    # ##########################################################################
    # #                                                                        #
    # # base translator overrides                                              #
    # #                                                                        #
    # ##########################################################################

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        self.document = ''.join(self.body)

    def visit_Text(self, node):
        text = node.astext()
        self.body.append(text)

    def depart_Text(self, node):
        pass

    def unknown_visit(self, node):
        raise NotImplementedError('unknown node: ' + node.__class__.__name__)
