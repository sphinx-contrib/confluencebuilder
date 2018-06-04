# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2017 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

CONFLUENCE_DEFAULT_MARGIN_OFFSET = 30
EXPERIMENTAL_QUOTE_KEYWORD = 'SCCBCSFTQUOTEFLAG'

class ConfluenceExperimentalQuoteSupport:
    """
    confluence experimental quote support class

    This class is used to assist in providing expected reStructuredText Markup
    quote indentation support into a published Confluence page. This utility
    class is designed to support the building of Wiki-generated document
    content and process a Confluence-converted storage format content to contain
    expected paragraph margins. When generating a Wiki-format page, paragraphs
    to be quoted should be 'flag'ed. After building a document, the Wiki-format
    page is provided to Confluence to generate a Storage-format page. This page
    is then 'process'ed to adjust paragraph margins to expected sizes.
    """

    @staticmethod
    def flag(level):
        """
        flag a document with a quote keyword

        The keyword includes a fixed-string, the two-length level value (to
        identify quote level) and a space character (markup processing).
        """
        return '%s%02d ' % (EXPERIMENTAL_QUOTE_KEYWORD, level)

    @staticmethod
    def process(data):
        """
        process a document for quote keywords to handle quote levels

        Split the document's content based on paragraph-prefixed keywords. The
        paragraph tag will be replaced with a new paragraph tag with a
        margin-modified style.
        """
        parts = data.split('<p>' + EXPERIMENTAL_QUOTE_KEYWORD)
        for idx, part in enumerate(parts[1:]):
            margin = CONFLUENCE_DEFAULT_MARGIN_OFFSET * int(part[:2])
            part_data = part[3:] # 2 (level) + 1 (space)
            parts[idx+1] = \
                '<p style="margin-left: %d.0px">%s' % (margin, part_data)

        return ''.join(parts);
