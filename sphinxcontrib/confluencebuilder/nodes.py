# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2019-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from docutils import nodes


class confluence_expand(nodes.Element):
    """
    confluence expand node

    A Confluence builder defined expand node serves as a hint to wrap content
    using Confluence's expand macro.
    """


class confluence_footer(nodes.General, nodes.Element):
    """
    confluence footer node

    A Confluence builder defined footer node provides additional generates
    nodes such as navigational nodes (e.g. next, previous, etc.) for the bottom
    of a document.
    """


class confluence_header(nodes.General, nodes.Element):
    """
    confluence header node

    A Confluence builder defined header node provides additional generates
    nodes such as navigational nodes (e.g. next, previous, etc.) for the top of
    a document.
    """


class confluence_metadata(nodes.Element):
    """
    confluence metadata node

    A Confluence builder defined metadata node holds metadata information for a
    given document.
    """


class confluence_page_generation_notice(nodes.TextElement):
    """
    confluence page generation notice node

    A Confluence builder defined page generation notice node, used to create a
    helpful message for users to indicate that the document's content has been
    generated.
    """


class confluence_source_link(nodes.Element, nodes.Structural):
    """
    confluence source link node

    Provides a source link node to hint at the creation of a reference which
    points to a generation document's original source document (or source
    location).

    Args:
        rawsource: raw text from which this element was constructed
        *children: list of child nodes
        **attributes: dictionary of attribute to apply to the element

    Attributes:
        params: dictionary of parameters to configure the node
    """
    def __init__(self, rawsource='', *children, **attributes):
        nodes.Element.__init__(self, rawsource, *children, **attributes)
        self.params = {}


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
    def __init__(self, rawsource='', *children, **attributes):
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
    def __init__(self, rawsource='', *children, **attributes):
        nodes.Element.__init__(self, rawsource, *children, **attributes)
        self.params = {}
