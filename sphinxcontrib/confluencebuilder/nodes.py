# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from docutils import nodes


# name for this extension's custom node parameters
CONFLUENCE_PARAMS_KEY = 'confluence-params'


class ConfluenceParams(nodes.Element):
    """
    confluence parameter-holding node

    A utility node class which helps setup tracking "parameters" entries inside
    a Element's attribute list, which can be forwarded to parameter entries
    for Confluence macro building.

    Args:
        rawsource: raw text from which this element was constructed
        *children: list of child nodes
        **attributes: dictionary of attribute to apply to the element

    Attributes:
        params: the tracked confluence parameters
    """
    def __init__(self, rawsource='', *children, **attributes):
        nodes.Element.__init__(self, rawsource, *children, **attributes)
        self.params = self.attributes.setdefault(CONFLUENCE_PARAMS_KEY, {})


class confluence_doc_card(nodes.Structural, ConfluenceParams):
    """
    confluence document card node

    A Confluence builder defined document card node, used to help add
    Confluence document-CARD for a block section.
    """


class confluence_doc_card_inline(nodes.Inline, ConfluenceParams):
    """
    confluence document card inline node

    A Confluence builder defined document card inline node, used to help add
    Confluence document-CARD for an inlined section of a paragraph.
    """


class confluence_emoticon_inline(nodes.Inline, nodes.TextElement):
    """
    confluence emoticon inline node

    A Confluence builder defined emoticon inline node, used to help manage
    emoticon content designed for an inlined section of a paragraph.
    """


class confluence_excerpt(nodes.Structural, ConfluenceParams):
    """
    confluence excerpt node

    A Confluence builder defined excerpt node serves as a hint to wrap content
    using Confluence's excerpt macro.
    """


class confluence_excerpt_include(nodes.Structural, ConfluenceParams):
    """
    confluence excerpt include node

    A Confluence builder defined excerpt include node serves as a hint to
    inject a Confluence's excerpt include macro into a page.
    """


class confluence_expand(nodes.Body, nodes.Element):
    """
    confluence expand node

    A Confluence builder defined expand node serves as a hint to wrap content
    using Confluence's expand macro.
    """


class confluence_footer(nodes.Decorative, nodes.Element):
    """
    confluence footer node

    A Confluence builder defined footer node provides additional generates
    nodes such as navigational nodes (e.g. next, previous, etc.) for the bottom
    of a document.
    """


class confluence_header(nodes.Decorative, nodes.Element):
    """
    confluence header node

    A Confluence builder defined header node provides additional generates
    nodes such as navigational nodes (e.g. next, previous, etc.) for the top of
    a document.
    """

class confluence_html(nodes.TextElement):
    """
    confluence html node

    A Confluence builder defined HTML node, used to help manage HTML content
    designed for an HTML macro.
    """

class confluence_metadata(nodes.Invisible, nodes.Special, ConfluenceParams):
    """
    confluence metadata node

    A Confluence builder defined metadata node holds metadata information for a
    given document.
    """


class confluence_newline(nodes.Structural, nodes.Element):
    """
    confluence newline node

    A Confluence builder defined newline node which provides a convenience hint
    that a newline should be injected into a document (for users not wanted to
    define a custom raw type).
    """


class confluence_latex_block(nodes.TextElement):
    """
    confluence latex block node

    A Confluence builder defined LaTeX block node, used to help manage LaTeX
    content designed for a block/section.
    """


class confluence_latex_inline(nodes.Inline, nodes.TextElement):
    """
    confluence latex inline node

    A Confluence builder defined LaTeX inline node, used to help manage LaTeX
    content designed for an inlined section of a paragraph.
    """


class confluence_link_card(nodes.Structural, ConfluenceParams):
    """
    confluence link card node

    A Confluence builder defined link card node, used to help add
    Confluence link-CARD for a block section.
    """


class confluence_link_card_inline(nodes.Inline, ConfluenceParams):
    """
    confluence card inline node

    A Confluence builder defined inline card node, used to help add
    Confluence link-CARD for an inlined section of a paragraph.
    """


class confluence_mathjax_block(nodes.TextElement):
    """
    confluence mathjax block node

    A Confluence builder defined MathJax block node, used to help manage MathJax
    content designed for a block/section.
    """


class confluence_mathjax_inline(nodes.Inline, nodes.TextElement):
    """
    confluence mathjax inline node

    A Confluence builder defined MathJax inline node, used to help manage MathJax
    content designed for an inlined section of a paragraph.
    """


class confluence_mention_inline(nodes.Inline, nodes.TextElement):
    """
    confluence mention inline node

    A Confluence builder defined mention inline node, used to help add
    Confluence @mentions for an inlined section of a paragraph.
    """


class confluence_status_inline(nodes.Inline, ConfluenceParams):
    """
    confluence status inline node

    A Confluence builder defined status inline node, used to help add
    Confluence status macros for an inlined section of a paragraph.
    """


class confluence_page_generation_notice(nodes.TextElement):
    """
    confluence page generation notice node

    A Confluence builder defined page generation notice node, used to create a
    helpful message for users to indicate that the document's content has been
    generated.
    """


class confluence_source_link(nodes.Structural, ConfluenceParams):
    """
    confluence source link node

    Provides a source link node to hint at the creation of a reference which
    points to a generation document's original source document (or source
    location).
    """


class confluence_toc(nodes.Structural, ConfluenceParams):
    """
    confluence toc node

    Provides a Confluence's TOC macro; an alternative to Sphinx's TOC and
    reStructuredText's contents directive.
    """


class jira(nodes.Inline, ConfluenceParams):
    """
    jira (query) node

    Defines a "JIRA" node to represent a Confluence JIRA macro configured to
    display a prepared JQL query.
    """


class jira_issue(nodes.Inline, ConfluenceParams):
    """
    jira (single) issue node

    Defines a "JIRA" node to represent a Confluence JIRA macro configured to
    display a single JIRA issue.
    """


def confluence_parameters_fetch(node):
    """
    fetch confluence parameters tracked on a node

    This call will look at the node's attributes and extract the
    Confluence-specific parameters (dictionary) from the instance.

    Args:
        node: the node holding Confluence-specific parameters

    Return:
        the parameters dictionary
    """

    return node.attributes[CONFLUENCE_PARAMS_KEY]
