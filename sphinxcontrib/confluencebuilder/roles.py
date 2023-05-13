# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

"""
See also docutils roles:

    https://docutils.sourceforge.io/docs/howto/rst-roles.html#define-the-role-function
"""

from docutils import nodes
from sphinxcontrib.confluencebuilder.nodes import confluence_doc_card_inline
from sphinxcontrib.confluencebuilder.nodes import confluence_emoticon_inline
from sphinxcontrib.confluencebuilder.nodes import confluence_latex_inline
from sphinxcontrib.confluencebuilder.nodes import confluence_link_card_inline
from sphinxcontrib.confluencebuilder.nodes import confluence_mention_inline
from sphinxcontrib.confluencebuilder.nodes import confluence_status_inline
from sphinxcontrib.confluencebuilder.nodes import jira_issue
from sphinx.roles import XRefRole


ConfluenceDocRole = XRefRole(nodeclass=confluence_doc_card_inline,
    innernodeclass=nodes.inline, warn_dangling=True)


def ConfluenceEmoticonRole(name, rawtext, text, lineno, inliner, options=None, content=None):
    """
    a confluence emoticon role

    Defines an inline Confluence emoticon role where users can inject inlined
    emoticon macros.

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

    node = confluence_emoticon_inline(rawsource=text, text=text)

    return [node], []


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


def ConfluenceLinkRole(name, rawtext, text, lineno, inliner, options=None, content=None):
    """
    a confluence link role

    Defines an inline Confluence link role where users can inject inlined
    card link (v2 editor) for a target link.

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

    node = confluence_link_card_inline(rawsource=text, text=text)
    node.params['href'] = text

    return [node], []


def ConfluenceMentionRole(name, rawtext, text, lineno, inliner, options=None, content=None):
    """
    a confluence mention role

    Defines an inline Confluence mention role where users can inject inlined
    @mentions.

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

    node = confluence_mention_inline(rawsource=text, text=text)

    return [node], []


def ConfluenceStatusRole(name, rawtext, text, lineno, inliner, options=None, content=None):
    """
    a confluence status role

    Defines an inline Confluence status role where users can inject inlined
    status macros.

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

    color = ''
    outlined = False

    try:
        leading_txt, opts = text.rsplit(' ', 1)

        parse_opts = False
        if opts.startswith('<') and opts.endswith('>'):
            parse_opts = True
        elif opts.startswith('[') and opts.endswith(']'):
            parse_opts = True
            outlined = True

        if parse_opts:
            text = leading_txt
            color = opts[1:-1]
    except ValueError:
        pass

    node = confluence_status_inline(rawsource=text, text=text)
    node.params['color'] = color
    node.params['title'] = text
    if outlined:
        node.params['subtle'] = 'true'

    return [node], []


def ConfluenceStrikeRole(name, rawtext, text, lineno, inliner, options=None, content=None):
    """
    a confluence strike role

    Defines an inline Confluence strike role where users can inject inlined
    node to styled with a strikethrough.

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

    node = nodes.inline(rawsource=text, text=text, classes=['strike'])

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
