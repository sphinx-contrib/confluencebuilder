# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)

See also docutils roles:

    https://docutils.sourceforge.io/docs/howto/rst-roles.html#define-the-role-function
"""

from sphinxcontrib.confluencebuilder.nodes import confluence_latex_inline
from sphinxcontrib.confluencebuilder.nodes import jira_issue


def ConfluenceLatexRole(name, rawtext, text, lineno, inliner, options=None, content=None):
    """
    a confluence latex role

    Defines an inline Confluence LaTeX role where users can inject inlined
    LaTeX content, if their instance supports a LaTeX macro.

    Args:
        name: local name of the interpreted text role
        rawtext: the entire interpreted text construct
        text: the interpreted text content
        lineno: the line number where the interpreted text beings
        inliner: inliner object that called the role function
        options: dictionary of directive options for customization
        content: list of strings, the directive content for customization

    Returns:
        returns a tuple include a list of nodes and a list of system messages
    """

    node = confluence_latex_inline(rawsource=text, text=text)

    return [node], []


def JiraRole(name, rawtext, text, lineno, inliner, options=None, content=None):
    """
    a jira role

    Defines an inline Jira role where users can inject a Jira issue macro inside
    a block of text.

    Args:
        name: local name of the interpreted text role
        rawtext: the entire interpreted text construct
        text: the interpreted text content
        lineno: the line number where the interpreted text beings
        inliner: inliner object that called the role function
        options: dictionary of directive options for customization
        content: list of strings, the directive content for customization

    Returns:
        returns a tuple include a list of nodes and a list of system messages
    """

    node = jira_issue()
    node.params['key'] = text
    node.params['showSummary'] = 'false'

    return [node], []
