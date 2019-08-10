# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2019 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from docutils import nodes

class ConfluenceNavigationNode(nodes.General, nodes.Element):

    """
    confluence navigational node

    A Confluence builder defined navigational node provides information on how
    to manipulate documents to add navigational enhancements (e.g. next,
    previous, etc.) at the top or bottom of pages (based on user configuration).

    Attributes:
        bottom: show navigation information at the bottom of a document
        top: show navigation information at the top of a document
    """
    def __init__(self):
        nodes.Element.__init__(self)

        self.bottom = False
        self.top = False
