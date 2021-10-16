# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2019-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
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


class confluence_expand(nodes.Element):
    """
    confluence expand node

    A Confluence builder defined expand node serves as a hint to wrap content
    using Confluence's expand macro.
    """


class confluence_metadata(nodes.Element):
    """
    confluence metadata node

    A Confluence builder defined metadata node holds metadata information for a
    given document.
    """


class jira(nodes.Element, nodes.Structural):
    """
    jira (query) node

    Defines a "JIRA" node to represent a Confluence JIRA macro configured to
    display a prepared JQL query.

    Args:
        rawsource: raw text from which this element was constructed
        *children: list of child nodes
        **attributes: dictionary of attribute to apply to the element

    Attributes:
        params: dictionary of parameters to pass into a jira macro
    """

    def __init__(self, rawsource="", *children, **attributes):
        nodes.Element.__init__(self, rawsource, *children, **attributes)
        self.params = {}


class jira_issue(nodes.Element, nodes.Structural):
    """
    jira (single) issue node

    Defines a "JIRA" node to represent a Confluence JIRA macro configured to
    display a single JIRA issue.

    Args:
        rawsource: raw text from which this element was constructed
        *children: list of child nodes
        **attributes: dictionary of attribute to apply to the element

    Attributes:
        params: dictionary of parameters to pass into a jira macro
    """

    def __init__(self, rawsource="", *children, **attributes):
        nodes.Element.__init__(self, rawsource, *children, **attributes)
        self.params = {}
